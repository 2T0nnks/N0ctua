from datetime import datetime
from .ui import format_error_message, format_chat_message, format_prompt
from .utils.helpers import clear_screen
from .session import SessionError
from .ui.formatting import Fore, Style

class CommandHandler:
    def __init__(self, peer):
        print("Initializing CommandHandler...")  # Debug
        self.peer = peer
        self.commands = {
            'c': self.handle_connect,
            'connect': self.handle_connect,
            'h': self.show_help,
            'help': self.show_help,
            'clear': lambda x: clear_screen() or True,
            'cls': lambda x: clear_screen() or True,
            'exit': self.handle_exit,
            'quit': self.handle_exit,
            'sair': self.handle_exit,
            'sessions': self.show_active_sessions
        }

    # Adicione este metodo
    def show_help(self, *args):
        """Shows help for available commands"""
        help_text = f"""
{Fore.CYAN}=== Available Commands ==={Style.RESET_ALL}
    {Fore.GREEN}c, connect{Fore.RESET} <string>  - Connects to another peer using the connection string
    {Fore.GREEN}sessions{Fore.RESET}           - Shows information about active sessions
    {Fore.GREEN}h, help{Fore.RESET}             - Shows this help message
    {Fore.GREEN}clear, cls{Fore.RESET}          - Clears the screen
    {Fore.GREEN}exit, quit, sair{Fore.RESET}    - Closes the program
        """
        self.peer.message_handler.print_message(help_text)
        return True

    def show_active_sessions(self, *args):
        """Shows currently active sessions"""
        try:
            active_sessions = []
            for socket, (peer_id, address, session_id) in self.peer.peers.items():
                if self.peer.session_manager.is_session_valid(session_id):
                    session_info = self.peer.session_manager.get_session_info(session_id)
                    active_sessions.append(f"Peer: {peer_id}, Session: {session_id[:8]}..., "
                                           f"Created: {session_info['created_at'].strftime('%H:%M:%S')}")

            if active_sessions:
                self.peer.message_handler.print_message(
                    format_chat_message("System", "Active sessions:")
                )
                for session in active_sessions:
                    self.peer.message_handler.print_message(
                        format_chat_message("System", f"  - {session}")
                    )
            else:
                self.peer.message_handler.print_message(
                    format_chat_message("System", "No active sessions")
                )
            return True
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error showing sessions: {e}")
            )
            return True

    def process_user_input(self, user_input):
        """Processes user input with session validation"""
        try:
            print(f"CommandHandler processing: {user_input}")  # Debug

            if not user_input:
                return True

            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            # Check session validity for all peers except for connect command
            if command not in ['c', 'connect', 'help', 'h', 'clear', 'cls', 'sessions']:
                invalid_sessions = []
                for socket, (peer_id, address, session_id) in self.peer.peers.items():
                    if not self.peer.session_manager.is_session_valid(session_id):
                        invalid_sessions.append((socket, peer_id, session_id))

                # Handle invalid sessions
                for socket, peer_id, session_id in invalid_sessions:
                    self.peer.message_handler.print_message(
                        format_error_message(f"[-] Invalid session detected for {peer_id}")
                    )
                    self.peer.remove_peer(socket)

                if invalid_sessions and not self.peer.peers:
                    self.peer.message_handler.print_message(
                        format_error_message("[-] No valid peer connections available")
                    )
                    return True

            if command in self.commands:
                return self.commands[command](args)

            # If it is not a command, it is a message
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"{self.peer.peer_id}: {user_input}"
            formatted_message = format_chat_message(self.peer.peer_id, user_input)
            self.peer.message_handler.print_message(formatted_message)

            if self.peer.peers:
                # Verify sessions before broadcasting
                valid_peers = {
                    socket: data for socket, data in self.peer.peers.items()
                    if self.peer.session_manager.is_session_valid(data[2])
                }

                if valid_peers:
                    self.peer.network.broadcast_message(full_message)
                else:
                    self.peer.message_handler.print_message(
                        format_error_message("[-] No valid peer connections available")
                    )
            return True

        except SessionError as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Session error: {e}")
            )
            return True
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error processing input: {e}")
            )
            return True

    def handle_connect(self, args):
        """Handles the connect command with session creation"""
        if not args:
            self.peer.message_handler.print_message(
                format_error_message("[-] Usage: connect <connection_string>")
            )
            return True

        try:
            return self.peer.connect_to_peer(args[0])
        except SessionError as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Session error during connection: {e}")
            )
            return True
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error connecting to peer: {e}")
            )
            return True

    def handle_exit(self, *args):
        """Handles the exit command and cleans up sessions"""
        try:
            # Invalidate all active sessions
            for socket, (peer_id, address, session_id) in self.peer.peers.items():
                try:
                    self.peer.session_manager.invalidate_session(session_id)
                except:
                    pass  # Ignore errors during cleanup

            self.peer.running = False
            return False
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error during exit: {e}")
            )
            return False