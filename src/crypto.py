import secrets
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    def __init__(self):
        self.generate_keys()

    def generate_keys(self):
        """Generates the RSA key pair"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self):
        """Returns the public key in PEM format"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def decrypt_aes_key(self, encrypted_aes_key):
        """Decrypts the AES key using the RSA private key"""
        return self.private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_aes_key(self, aes_key, public_key_pem):
        """Encrypts the AES key using the provided public key"""
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
        """Creates a new AES-GCM instance with a random key"""
        aes_key = AESGCM.generate_key(bit_length=256)
        return aes_key, AESGCM(aes_key)

    @staticmethod
    def encrypt_message(aes_gcm, message):
        """Encrypts a message using AES-GCM"""
        nonce = secrets.token_bytes(12)
        encrypted_message = aes_gcm.encrypt(
            nonce,
            message.encode(),
            None
        )
        return nonce + encrypted_message

    @staticmethod
    def decrypt_message(aes_gcm, encrypted_data):
        """Decrypts a message using AES-GCM"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aes_gcm.decrypt(nonce, ciphertext, None).decode()
