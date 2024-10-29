import threading

from .formatting import format_prompt


class MessageHandler:
    def __init__(self):
        self.print_lock = threading.Lock()

    def print_message(self, message, end='\n'):
        """Imprime mensagens de forma thread-safe"""
        with self.print_lock:
            print(message, end=end, flush=True)

    def print_with_prompt(self, message, peer_id, end='\n'):
        """Imprime mensagem e restaura o prompt"""
        with self.print_lock:
            print(message)
            print(format_prompt(peer_id), end=end, flush=True)
