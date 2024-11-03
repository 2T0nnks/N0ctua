from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class SessionStatus(Enum):
    ACTIVE = "active"
    ROTATING = "rotating"
    INVALIDATED = "invalidated"

@dataclass
class TransitionToken:
    token: str
    old_session: str
    new_session: str
    expires_at: datetime
    used: bool = False