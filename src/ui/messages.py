import threading

from .formatting import format_prompt


class MessageHandler:
    def __init__(self):
        self.print_lock = threading.Lock()

    def print_message(self, message, end='\n'):
        """Prints messages in a thread-safe manner"""
        with self.print_lock:
            print(message, end=end, flush=True)

    def print_with_prompt(self, message, peer_id, end='\n'):
        """Prints a message and restores the prompt"""
        with self.print_lock:
            print(message)
            print(format_prompt(peer_id), end=end, flush=True)
