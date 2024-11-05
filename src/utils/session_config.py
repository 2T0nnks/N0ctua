import os

class SessionConfig:
    # Default settings
    DEFAULT_CONFIG = {
        'token_lifetime': 30,        # Token duration in seconds
        'notification_window': 10,   # Notification time before rotation in seconds
        'max_queue_size': 100,       # Maximum number of messages in the queue
        'max_queue_age': 30,         # Maximum age of messages in seconds
        'rotation_interval': 1800    # Rotation interval in seconds (30 minutes)
    }

    @classmethod
    def get_config(cls):
        """
        Returns session configurations, allowing overrides via environment variables
        """
        config = cls.DEFAULT_CONFIG.copy()

        # Environment variable mapping
        env_mapping = {
            'N0CTUA_TOKEN_LIFETIME': ('token_lifetime', int),
            'N0CTUA_NOTIFICATION_WINDOW': ('notification_window', int),
            'N0CTUA_MAX_QUEUE_SIZE': ('max_queue_size', int),
            'N0CTUA_MAX_QUEUE_AGE': ('max_queue_age', int),
            'N0CTUA_ROTATION_INTERVAL': ('rotation_interval', int)
        }

        # Applies environment variable settings if they exist
        for env_var, (config_key, type_cast) in env_mapping.items():
            if env_var in os.environ:
                try:
                    config[config_key] = type_cast(os.environ[env_var])
                except ValueError as e:
                    print(f"Warning: Invalid value for {env_var}: {e}")

        return config

    @classmethod
    def validate_config(cls, config):
        """
        Validates the configurations
        """
        validations = {
            'token_lifetime': (5, 300),       # Between 5s and 5min
            'notification_window': (5, 60),   # Between 5s and 1min
            'max_queue_size': (10, 1000),     # Between 10 and 1000 messages
            'max_queue_age': (10, 300),       # Between 10s and 5min
            'rotation_interval': (300, 7200)  # Between 5min and 2h
        }

        for key, (min_val, max_val) in validations.items():
            value = config.get(key)
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"Invalid {key}: {value}. Must be between {min_val} and {max_val}"
                )

        return True
