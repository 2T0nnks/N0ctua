from datetime import datetime
from .ui import format_error_message, format_chat_message, format_prompt
from .utils.helpers import clear_screen  # Alterado para importar diretamente do helpers

class CommandHandler:
    def __init__(self, peer):
        self.peer = peer
        self.commands = {
            'c': self.handle_connect,
            'connect': self.handle_connect,
            'h': self.show_help,
            'help': self.show_help,
            'clear': clear_screen,
            'cls': clear_screen,
            'exit': self.handle_exit,
            'quit': self.handle_exit,
            'sair': self.handle_exit
        }

    def process_user_input(self, user_input):
        """Processa a entrada do usuário"""
        try:
            if not user_input:
                return True

            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            if command in self.commands:
                return self.commands[command](args)

            # Se não for comando, é uma mensagem
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"{self.peer.peer_id}: {user_input}"
            formatted_message = format_chat_message(self.peer.peer_id, user_input)
            self.peer.message_handler.print_message(formatted_message)

            if self.peer.peers:
                self.peer.network.broadcast_message(full_message)
            return True

        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Erro ao processar entrada: {e}")
            )
            return True

    def show_help(self, *args):
        """Mostra a ajuda dos comandos disponíveis"""
        from .ui.formatting import Fore, Style
        help_text = f"""
{Fore.CYAN}=== Comandos Disponíveis ==={Style.RESET_ALL}
    {Fore.GREEN}c, connect{Fore.RESET} <string>  - Conecta a outro peer usando a string de conexão
    {Fore.GREEN}h, help{Fore.RESET}             - Mostra esta mensagem de ajuda
    {Fore.GREEN}clear, cls{Fore.RESET}          - Limpa a tela
    {Fore.GREEN}exit, quit, sair{Fore.RESET}    - Encerra o programa
        """
        self.peer.message_handler.print_message(help_text)
        return True

    def handle_connect(self, args):
        """Trata o comando de conexão"""
        if not args:
            self.peer.message_handler.print_message(
                format_error_message("[-] Use: connect <string_conexao>")
            )
            return False
        return self.peer.connect_to_peer(args[0])

    def handle_exit(self, *args):
        """Trata o comando de saída"""
        self.peer.running = False
        return False
