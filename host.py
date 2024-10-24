import socket
import threading
import random
from cryptography.fernet import Fernet

# Carrega a chave de criptografia
def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())

PORT = 65432  # Porta fixa ou aleatória

def handle_client(client_socket):
    """Recebe e decripta mensagens do cliente."""
    while True:
        try:
            message = client_socket.recv(1024)
            decrypted_message = fernet.decrypt(message).decode()
            print(f"Cliente: {decrypted_message}")
        except:
            print("Cliente desconectado.")
            client_socket.close()
            break

def send_messages(client_socket):
    """Envia mensagens criptografadas para o cliente."""
    while True:
        message = input("Você: ")
        encrypted_message = fernet.encrypt(message.encode())
        client_socket.send(encrypted_message)

def start_host():
    """Inicia o host e gera o código de acesso."""
    host = socket.gethostbyname(socket.gethostname())
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, PORT))
    server_socket.listen(1)

    # Gera um código de acesso aleatório
    access_code = str(random.randint(1000, 9999))
    print(f"Link de acesso: {host}:{PORT}")
    print(f"Código de acesso: {access_code}")

    client_socket, addr = server_socket.accept()
    print(f"Conectado com {addr}")

    # Verifica o código de acesso enviado pelo cliente
    client_code = client_socket.recv(1024).decode()
    if client_code == access_code:
        client_socket.send(b"OK")  # Envia confirmação
        print("Cliente autenticado com sucesso!")
    else:
        client_socket.send(b"ERRO")  # Envia erro e encerra a conexão
        print("Código de acesso incorreto. Desconectando...")
        client_socket.close()
        return

    # Inicia threads para enviar e receber mensagens
    thread_receive = threading.Thread(target=handle_client, args=(client_socket,))
    thread_receive.start()

    thread_send = threading.Thread(target=send_messages, args=(client_socket,))
    thread_send.start()

if __name__ == "__main__":
    start_host()
