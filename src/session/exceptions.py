class SessionError(Exception):
    """Base exception for session-related errors"""
    pass

class SessionRotationError(SessionError):
    """Exception raised for session rotation errors"""
    pass

class SessionValidationError(SessionError):
    """Exception raised for session validation errors"""
    pass