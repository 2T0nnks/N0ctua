# config.py
import os
from typing import Dict, Any

# Default session configuration
SESSION_CONFIG = {
    'token_lifetime': 30,  # Duration of transition tokens in seconds
    'notification_window': 10,  # Time before rotation to notify peers in seconds
    'max_queue_size': 100,  # Maximum number of messages to queue during rotation
    'max_queue_age': 30,  # Maximum age of queued messages in seconds
    'rotation_interval': 1800  # Time between session rotations (30 minutes)
}


def get_session_config() -> Dict[str, Any]:
    """
    Retrieves session configuration with environment variable overrides.

    Environment Variables:
        N0CTUA_TOKEN_LIFETIME: Override token lifetime
        N0CTUA_NOTIFICATION_WINDOW: Override notification window
        N0CTUA_MAX_QUEUE_SIZE: Override maximum queue size
        N0CTUA_MAX_QUEUE_AGE: Override maximum queue message age
        N0CTUA_ROTATION_INTERVAL: Override session rotation interval

    Returns:
        Dict containing the session configuration
    """
    config = SESSION_CONFIG.copy()

    # Map environment variables to configuration keys
    env_mappings = {
        'N0CTUA_TOKEN_LIFETIME': ('token_lifetime', int),
        'N0CTUA_NOTIFICATION_WINDOW': ('notification_window', int),
        'N0CTUA_MAX_QUEUE_SIZE': ('max_queue_size', int),
        'N0CTUA_MAX_QUEUE_AGE': ('max_queue_age', int),
        'N0CTUA_ROTATION_INTERVAL': ('rotation_interval', int)
    }

    # Apply environment overrides
    for env_var, (config_key, type_cast) in env_mappings.items():
        if env_var in os.environ:
            try:
                config[config_key] = type_cast(os.environ[env_var])
            except ValueError as e:
                print(f"Warning: Invalid value for {env_var}: {e}")

    return config


# Optional: Configuration validation
def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validates the session configuration values.

    Args:
        config: Configuration dictionary to validate

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If any configuration value is invalid
    """
    # Validate token lifetime
    if config['token_lifetime'] < 5 or config['token_lifetime'] > 300:
        raise ValueError("token_lifetime must be between 5 and 300 seconds")

    # Validate notification window
    if config['notification_window'] < 5 or config['notification_window'] > 60:
        raise ValueError("notification_window must be between 5 and 60 seconds")

    # Validate queue size
    if config['max_queue_size'] < 10 or config['max_queue_size'] > 1000:
        raise ValueError("max_queue_size must be between 10 and 1000 messages")

    # Validate queue age
    if config['max_queue_age'] < 10 or config['max_queue_age'] > 300:
        raise ValueError("max_queue_age must be between 10 and 300 seconds")

    # Validate rotation interval
    if config['rotation_interval'] < 300 or config['rotation_interval'] > 7200:
        raise ValueError("rotation_interval must be between 300 and 7200 seconds")

    return True


# Usage example
def initialize_session_config() -> Dict[str, Any]:
    """
    Initializes and validates session configuration.

    Returns:
        Dict containing validated session configuration

    Raises:
        ValueError: If configuration validation fails
    """
    config = get_session_config()
    if validate_config(config):
        return config