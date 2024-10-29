import secrets
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    def __init__(self):
        self.generate_keys()

    def generate_keys(self):
        """Gera o par de chaves RSA"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self):
        """Retorna a chave pública em formato PEM"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def decrypt_aes_key(self, encrypted_aes_key):
        """Decripta a chave AES usando a chave privada RSA"""
        return self.private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_aes_key(self, aes_key, public_key_pem):
        """Encripta a chave AES usando a chave pública fornecida"""
        remote_public_key = serialization.load_pem_public_key(public_key_pem)
        return remote_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    @staticmethod
    def create_aes_gcm():
        """Cria uma nova instância AES-GCM com uma chave aleatória"""
        aes_key = AESGCM.generate_key(bit_length=256)
        return aes_key, AESGCM(aes_key)

    @staticmethod
    def encrypt_message(aes_gcm, message):
        """Encripta uma mensagem usando AES-GCM"""
        nonce = secrets.token_bytes(12)
        encrypted_message = aes_gcm.encrypt(
            nonce,
            message.encode(),
            None
        )
        return nonce + encrypted_message

    @staticmethod
    def decrypt_message(aes_gcm, encrypted_data):
        """Decripta uma mensagem usando AES-GCM"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aes_gcm.decrypt(nonce, ciphertext, None).decode()