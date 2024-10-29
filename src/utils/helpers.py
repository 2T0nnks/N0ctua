import os
import socket
import secrets

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_available_port():
    """Encontra uma porta disponível para escuta"""
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_socket.bind(('', 0))
    _, port = temp_socket.getsockname()
    temp_socket.close()
    return port

def generate_id(prefix="Peer"):
    """Gera um ID único para o peer"""
    return f"{prefix}_{secrets.token_hex(2)}"

def parse_connection_string(conn_str):
    """Analisa a string de conexão no formato ip:port:secret"""
    try:
        if conn_str.count(':') != 2:
            raise ValueError("Formato inválido. Use: ip:port:secret")

        host, port, secret = conn_str.split(':')
        return host.strip(), int(port.strip()), secret.strip()
    except Exception as e:
        return None, None, None