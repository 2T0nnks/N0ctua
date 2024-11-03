import secrets
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from .models import SessionStatus, TransitionToken
from .exceptions import SessionError, SessionRotationError, SessionValidationError


class N0ctuaSessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.transition_tokens: Dict[str, TransitionToken] = {}
        self.message_queues: Dict[str, List[dict]] = {}
        self.rotation_schedule: Dict[str, datetime] = {}
        self.lock = threading.Lock()

        # Configuration settings
        self.config = {
            'token_lifetime': 30,  # seconds
            'notification_window': 10,  # seconds
            'max_queue_size': 100,  # messages
            'max_queue_age': 30,  # seconds
            'rotation_interval': 1800  # 30 minutes
        }

    def create_session(self, peer_id: str) -> str:
        """Creates a new session for a peer"""
        session_id = secrets.token_urlsafe(32)

        with self.lock:
            self.sessions[session_id] = {
                'peer_id': peer_id,
                'created_at': datetime.now(),
                'status': SessionStatus.ACTIVE,
                'operations_count': 0
            }

        return session_id

    def is_session_valid(self, session_id: str) -> bool:
        """Checks if a session is valid"""
        with self.lock:
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]
            return session['status'] == SessionStatus.ACTIVE

    def invalidate_session(self, session_id: str) -> None:
        """Invalidates a session"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['status'] = SessionStatus.INVALIDATED

    def update_session_peer_id(self, session_id: str, peer_id: str) -> None:
        """Updates the peer ID associated with a session"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['peer_id'] = peer_id

    def check_rotation_needed(self, session_id: str) -> bool:
        """Checks if session rotation is needed"""
        with self.lock:
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]
            session_age = (datetime.now() - session['created_at']).total_seconds()
            return session_age >= self.config['rotation_interval']

    def rotate_session(self, current_session_id: str) -> Tuple[str, str]:
        """Executes session rotation"""
        with self.lock:
            if current_session_id not in self.sessions:
                raise SessionError("Session not found")

            current_session = self.sessions[current_session_id]
            if current_session['status'] != SessionStatus.ACTIVE:
                raise SessionError("Session is not active")

            # Create new session
            new_session_id = secrets.token_urlsafe(32)
            new_session = current_session.copy()
            new_session['created_at'] = datetime.now()
            new_session['operations_count'] = 0

            # Create transition token
            transition_token = secrets.token_urlsafe(32)
            token_expiration = datetime.now() + timedelta(
                seconds=self.config['token_lifetime']
            )

            self.transition_tokens[transition_token] = TransitionToken(
                token=transition_token,
                old_session=current_session_id,
                new_session=new_session_id,
                expires_at=token_expiration
            )

            # Update states
            current_session['status'] = SessionStatus.INVALIDATED
            self.sessions[new_session_id] = new_session

            return new_session_id, transition_token

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Gets information about a session"""
        with self.lock:
            return self.sessions.get(session_id)

    def queue_message(self, session_id: str, message: dict) -> bool:
        """Queues a message during session rotation"""
        with self.lock:
            if session_id not in self.message_queues:
                self.message_queues[session_id] = []

            queue = self.message_queues[session_id]
            if len(queue) >= self.config['max_queue_size']:
                return False

            queue.append({
                'content': message,
                'timestamp': datetime.now()
            })
            return True

    def process_queued_messages(self, session_id: str) -> List[dict]:
        """Processes queued messages for a session"""
        with self.lock:
            if session_id not in self.message_queues:
                return []

            current_time = datetime.now()
            valid_messages = [
                msg['content'] for msg in self.message_queues[session_id]
                if (current_time - msg['timestamp']).total_seconds() <=
                   self.config['max_queue_age']
            ]

            del self.message_queues[session_id]
            return valid_messages