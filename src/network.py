from .crypto import CryptoManager
from .ui import format_error_message
from .session import SessionError


class NetworkManager:
    def __init__(self, peer):
        self.peer = peer

    def send_encrypted_message(self, socket, message, aes_gcm):
        """Sends encrypted message with size control and session validation"""
        try:
            # Verify if socket has a valid session
            if socket not in self.peer.peers:
                raise SessionError("No session found for socket")

            # Get session from peers dictionary
            peer_id, address, session_id = self.peer.peers[socket]

            # Check for session rotation
            if self.peer.session_manager.check_rotation_needed(session_id):
                # Perform session rotation
                try:
                    new_session_id, token = self.peer.session_manager.rotate_session(session_id)

                    # Queue message during rotation
                    self.peer.session_manager.queue_message(new_session_id, message)

                    # Update peers dictionary with new session
                    self.peer.peers[socket] = (peer_id, address, new_session_id)

                    # Send rotation notification to peer
                    rotation_notice = {
                        'type': 'session_rotation',
                        'token': token,
                        'new_session': new_session_id
                    }
                    # Encrypt and send rotation notice
                    encrypted_notice = CryptoManager.encrypt_message(aes_gcm, str(rotation_notice))
                    size_bytes = len(encrypted_notice).to_bytes(4, 'big')
                    socket.sendall(size_bytes + encrypted_notice)
                    return True

                except SessionError as e:
                    self.peer.message_handler.print_message(
                        format_error_message(f"[-] Session rotation failed: {e}")
                    )
                    return False

            # Normal message sending
            encrypted_data = CryptoManager.encrypt_message(aes_gcm, message)
            size_bytes = len(encrypted_data).to_bytes(4, 'big')
            socket.sendall(size_bytes + encrypted_data)
            return True

        except SessionError as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Session error: {e}")
            )
            return False
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error sending message: {e}")
            )
            return False

    def receive_encrypted_message(self, socket, aes_gcm):
        """Receives encrypted message with size control and session validation"""
        try:
            # Verify if socket has a valid session
            if socket not in self.peer.peers:
                raise SessionError("No session found for socket")

            # Get session information
            peer_id, address, session_id = self.peer.peers[socket]

            # Verify session validity
            if not self.peer.session_manager.is_session_valid(session_id):
                raise SessionError("Invalid session")

            size_data = socket.recv(4)
            if not size_data:
                return None

            msg_size = int.from_bytes(size_data, 'big')

            encrypted_data = b''
            remaining = msg_size
            while remaining > 0:
                chunk = socket.recv(min(remaining, 4096))
                if not chunk:
                    return None
                encrypted_data += chunk
                remaining -= len(chunk)

            decrypted_message = CryptoManager.decrypt_message(aes_gcm, encrypted_data)

            # Check if message is a session rotation notice
            try:
                message_data = eval(decrypted_message)
                if isinstance(message_data, dict) and message_data.get('type') == 'session_rotation':
                    # Handle session rotation
                    new_session_id = message_data['new_session']
                    token = message_data['token']

                    # Validate transition
                    if self.peer.session_manager.validate_transition(session_id, new_session_id, token):
                        # Update session in peers dictionary
                        self.peer.peers[socket] = (peer_id, address, new_session_id)

                        # Process any queued messages
                        queued_messages = self.peer.session_manager.process_queued_messages(new_session_id)
                        for queued_msg in queued_messages:
                            self.send_encrypted_message(socket, queued_msg, aes_gcm)

                        return None
            except:
                # If not a rotation notice, treat as normal message
                pass

            return decrypted_message

        except SessionError as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Session error: {e}")
            )
            return None
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error receiving message: {e}")
            )
            return None

    def broadcast_message(self, message, sender_socket=None):
        """Sends message to all connected peers with session validation"""
        peers_to_remove = []

        for peer_socket, (peer_id, address, session_id) in list(self.peer.peers.items()):
            if peer_socket != sender_socket:
                try:
                    # Verify session validity
                    if not self.peer.session_manager.is_session_valid(session_id):
                        peers_to_remove.append(peer_socket)
                        continue

                    # Get encryption context for this peer
                    aes_gcm = self.peer.crypto_contexts[peer_socket]
                    self.send_encrypted_message(peer_socket, message, aes_gcm)

                except Exception as e:
                    self.peer.message_handler.print_message(
                        format_error_message(f"\r[-] Error sending message to {peer_id}: {e}")
                    )
                    peers_to_remove.append(peer_socket)

        for peer_socket in peers_to_remove:
            self.peer.remove_peer(peer_socket)