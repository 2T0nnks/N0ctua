import os
import socket
import threading
import secrets
import sys
from datetime import datetime
from colorama import init, Fore, Style
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

init(autoreset=True)


class SecurePeer:
    def __init__(self, listen_port=None, peer_id=None):
        self.peer_id = peer_id or f"Peer_{secrets.token_hex(2)}"
        self.listen_port = listen_port or self.find_available_port()
        self.host = socket.gethostbyname(socket.gethostname())
        self.secret = secrets.token_urlsafe(16)
        self.peers = {}  # {socket: (peer_id, address)}
        self.print_lock = threading.Lock()
        self.running = True
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Gera par de chaves RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        # Comandos disponíveis
        self.commands = {
            'c': self.handle_connect,
            'connect': self.handle_connect,
            'help': self.show_help,
            'exit': self.handle_exit,
            'quit': self.handle_exit,
            'sair': self.handle_exit
        }

    def find_available_port(self):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.bind(('', 0))
        _, port = temp_socket.getsockname()
        temp_socket.close()
        return port

    def print_message(self, message, end='\n'):
        with self.print_lock:
            print(message, end=end, flush=True)

    def format_message(self, peer_id, message, include_timestamp=True):
        """Formata a mensagem com timestamp e ID do peer"""
        if include_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            return f"[{timestamp}] {peer_id}: {message}"
        return f"{peer_id}: {message}"

    def show_help(self, *args):
        help_text = f"""
{Fore.CYAN}=== Comandos Disponíveis ==={Style.RESET_ALL}
    {Fore.GREEN}c, connect{Fore.RESET} <string>  - Conecta a outro peer usando a string de conexão
    {Fore.GREEN}help{Fore.RESET}                - Mostra esta mensagem de ajuda
    {Fore.GREEN}exit, quit, sair{Fore.RESET}    - Encerra o programa

Para conectar, use o comando connect com a string de conexão mostrada acima.
Exemplo: connect 192.168.1.100:5000:abc123
"""
        self.print_message(help_text)
        return True

    def handle_connect(self, args):
        if not args:
            self.print_message(f"{Fore.RED}[-] Use: connect <string_conexao>{Style.RESET_ALL}")
            return True
        return self.connect_to_peer(args[0])

    def handle_exit(self, *args):
        self.running = False
        return False

    def parse_connection_string(self, conn_str):
        try:
            if conn_str.count(':') != 2:
                raise ValueError("Formato inválido. Use: ip:port:secret")
            host, port, secret = conn_str.split(':')
            return host.strip(), int(port.strip()), secret.strip()
        except Exception as e:
            self.print_message(f"{Fore.RED}[-] Erro ao parsear string de conexão: {e}{Style.RESET_ALL}")
            return None, None, None

    def connect_to_peer(self, connection_string):
        try:
            host, port, secret = self.parse_connection_string(connection_string)
            if not host or not port or not secret:
                return True

            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((host, port))

            # Envia o secret
            peer_socket.send(secret.encode())

            # Recebe a confirmação
            response = peer_socket.recv(1024).decode()
            if response != "OK":
                self.print_message(f"{Fore.RED}[-] Conexão rejeitada - secret inválido{Style.RESET_ALL}")
                peer_socket.close()
                return True

            # Envia nosso ID
            peer_socket.send(self.peer_id.encode())
            # Recebe o ID do peer remoto
            remote_peer_id = peer_socket.recv(1024).decode()

            # Armazena informações do peer
            self.peers[peer_socket] = (remote_peer_id, (host, port))
            self.print_message(f"{Fore.GREEN}[+] Conectado a {remote_peer_id}{Style.RESET_ALL}")

            # Inicia thread para receber mensagens
            thread = threading.Thread(target=self.handle_peer_messages, args=(peer_socket,))
            thread.daemon = True
            thread.start()

            return True

        except Exception as e:
            self.print_message(f"{Fore.RED}[-] Erro ao conectar ao peer: {e}{Style.RESET_ALL}")
            return True

    def handle_peer_connection(self, peer_socket, address):
        try:
            # Verifica o secret
            received_secret = peer_socket.recv(1024).decode()
            if received_secret != self.secret:
                peer_socket.send("ERROR".encode())
                peer_socket.close()
                return

            peer_socket.send("OK".encode())

            # Recebe o ID do peer remoto
            remote_peer_id = peer_socket.recv(1024).decode()
            # Envia nosso ID
            peer_socket.send(self.peer_id.encode())

            # Armazena informações do peer
            self.peers[peer_socket] = (remote_peer_id, address)
            self.print_message(f"\r{Fore.GREEN}[+] Peer {remote_peer_id} conectado de {address}{Style.RESET_ALL}")
            self.print_message(f"{self.peer_id}> ", end='')

            # Inicia o loop de recebimento de mensagens
            self.handle_peer_messages(peer_socket)

        except Exception as e:
            self.print_message(f"\r{Fore.RED}[-] Erro na conexão com {address}: {e}{Style.RESET_ALL}")
        finally:
            if peer_socket in self.peers:
                remote_peer_id = self.peers[peer_socket][0]
                del self.peers[peer_socket]
                try:
                    peer_socket.close()
                except:
                    pass
                self.print_message(f"\r{Fore.RED}[-] {remote_peer_id} desconectado{Style.RESET_ALL}")
                self.print_message(f"{self.peer_id}> ", end='')

    def handle_peer_messages(self, peer_socket):
        remote_peer_id = self.peers.get(peer_socket, (None, None))[0]
        while self.running and peer_socket in self.peers:
            try:
                message = peer_socket.recv(4096).decode()
                if not message:
                    break

                formatted_message = self.format_message(remote_peer_id, message)
                self.print_message(f"\r{Fore.BLUE}{formatted_message}{Style.RESET_ALL}")
                self.print_message(f"{self.peer_id}> ", end='')

            except Exception as e:
                self.print_message(
                    f"\r{Fore.RED}[-] Erro ao receber mensagem de {remote_peer_id}: {e}{Style.RESET_ALL}")
                break

        if peer_socket in self.peers:
            remote_peer_id = self.peers[peer_socket][0]
            del self.peers[peer_socket]
            try:
                peer_socket.close()
            except:
                pass
            self.print_message(f"\r{Fore.YELLOW}[-] Peer {remote_peer_id} desconectado{Style.RESET_ALL}")
            self.print_message(f"{self.peer_id}> ", end='')

    def broadcast_message(self, message):
        formatted_message = self.format_message(self.peer_id, message, include_timestamp=False)
        disconnected_peers = []

        for peer_socket in self.peers:
            try:
                peer_socket.send(formatted_message.encode())
            except:
                disconnected_peers.append(peer_socket)

        for peer_socket in disconnected_peers:
            if peer_socket in self.peers:
                remote_peer_id = self.peers[peer_socket][0]
                del self.peers[peer_socket]
                try:
                    peer_socket.close()
                except:
                    pass
                self.print_message(f"\r{Fore.YELLOW}[-] Peer {remote_peer_id} desconectado{Style.RESET_ALL}")

    def start_listening(self):
        """Inicia o socket de escuta para conexões de outros peers"""
        try:
            self.listen_socket.bind((self.host, self.listen_port))
            self.listen_socket.listen(5)

            self.print_message(f"""
{Fore.CYAN}{'=' * 20} Informações de Conexão {'=' * 20}{Style.RESET_ALL}
{Fore.GREEN}ID: {self.peer_id}
Endereço: {self.host}:{self.listen_port}
Secret: {self.secret}{Style.RESET_ALL}

{Fore.YELLOW}String de conexão (copie esta linha):{Style.RESET_ALL}
{Fore.GREEN}{self.host}:{self.listen_port}:{self.secret}{Style.RESET_ALL}

{Fore.CYAN}Digite 'help' para ver os comandos disponíveis{Style.RESET_ALL}
{'=' * 65}
""")

            while self.running:
                try:
                    peer_socket, address = self.listen_socket.accept()
                    thread = threading.Thread(target=self.handle_peer_connection, args=(peer_socket, address))
                    thread.daemon = True
                    thread.start()
                except socket.error:
                    break
        except Exception as e:
            self.print_message(f"{Fore.RED}[-] Erro ao iniciar escuta: {e}{Style.RESET_ALL}")

    def process_user_input(self, user_input):
        if not user_input:
            return True

        # Verifica se é um comando
        command = user_input.split()[0].lower()
        args = user_input.split()[1:] if len(user_input.split()) > 1 else []

        if command in self.commands:
            return self.commands[command](args)

        # Se não for comando, é uma mensagem para broadcast
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.print_message(f"\r{Fore.BLUE}[{timestamp}] {self.peer_id}: {user_input}{Style.RESET_ALL}")
        self.broadcast_message(user_input)
        return True

    def start(self):
        try:
            listen_thread = threading.Thread(target=self.start_listening)
            listen_thread.daemon = True
            listen_thread.start()

            while self.running:
                try:
                    user_input = input(f"{self.peer_id}> ").strip()
                    if not self.process_user_input(user_input):
                        break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.print_message(f"{Fore.RED}[-] Erro: {e}{Style.RESET_ALL}")

            self.running = False
            for peer_socket in list(self.peers.keys()):
                try:
                    peer_socket.close()
                except:
                    pass
            self.listen_socket.close()
            self.print_message(f"\n{Fore.YELLOW}[*] Chat encerrado{Style.RESET_ALL}")

        except Exception as e:
            self.print_message(f"{Fore.RED}[-] Erro durante a execução: {e}{Style.RESET_ALL}")


def main():
    try:
        peer_id = None
        listen_port = None

        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg.startswith('--id='):
                    peer_id = arg.split('=')[1]
                elif arg.startswith('--port='):
                    try:
                        listen_port = int(arg.split('=')[1])
                    except ValueError:
                        print(f"{Fore.RED}[-] Porta inválida{Style.RESET_ALL}")
                        return

        peer = SecurePeer(listen_port=listen_port, peer_id=peer_id)
        peer.start()

    except Exception as e:
        print(f"{Fore.RED}[-] Erro ao iniciar o peer: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()