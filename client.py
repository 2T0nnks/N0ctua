import socket
import threading
from cryptography.fernet import Fernet

# Carrega a chave de criptografia
def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())

def receive_messages(client_socket):
    """Recebe e decripta mensagens do host."""
    while True:
        try:
            message = client_socket.recv(1024)
            decrypted_message = fernet.decrypt(message).decode()
            print(f"Host: {decrypted_message}")
        except:
            print("Conexão com o host perdida.")
            client_socket.close()
            break

def send_messages(client_socket):
    """Envia mensagens criptografadas para o host."""
    while True:
        message = input("")
        encrypted_message = fernet.encrypt(message.encode())
        client_socket.send(encrypted_message)

def start_client(host, port):
    """Conecta-se ao host e inicia as threads de envio e recebimento."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, int(port)))

    # Solicita o código de acesso e envia para o host
    access_code = input("Digite o código de acesso: ")
    client_socket.send(access_code.encode())

    # Aguarda a resposta do host
    response = client_socket.recv(1024).decode()
    if response != "OK":
        print("Código de acesso incorreto. Encerrando conexão...")
        client_socket.close()
        return

    print("Conectado ao chat! Você pode enviar e receber mensagens.")

    # Inicia a thread para receber mensagens
    thread_receive = threading.Thread(target=receive_messages, args=(client_socket,))
    thread_receive.start()

    # Inicia a thread para enviar mensagens
    thread_send = threading.Thread(target=send_messages, args=(client_socket,))
    thread_send.start()

if __name__ == "__main__":
    host = input("Digite o IP do host: ")
    port = input("Digite a porta: ")

    start_client(host, port)
