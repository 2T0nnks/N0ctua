from .crypto import CryptoManager
from .ui import format_error_message


class NetworkManager:
    def __init__(self, peer):
        self.peer = peer

    def send_encrypted_message(self, socket, message, aes_gcm):
        """Sends encrypted message with size control"""
        try:
            encrypted_data = CryptoManager.encrypt_message(aes_gcm, message)
            size_bytes = len(encrypted_data).to_bytes(4, 'big')
            socket.sendall(size_bytes + encrypted_data)
            return True
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error sending message: {e}")
            )
            return False

    def receive_encrypted_message(self, socket, aes_gcm):
        """Receives encrypted message with size control"""
        try:
            size_data = socket.recv(4)
            if not size_data:
                return None

            msg_size = int.from_bytes(size_data, 'big')

            encrypted_data = b''
            remaining = msg_size
            while remaining > 0:
                chunk = socket.recv(min(remaining, 4096))
                if not chunk:
                    return None
                encrypted_data += chunk
                remaining -= len(chunk)

            return CryptoManager.decrypt_message(aes_gcm, encrypted_data)

        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error receiving message: {e}")
            )
            return None

    def broadcast_message(self, message, sender_socket=None):
        """Sends message to all connected peers"""
        peers_to_remove = []

        for peer_socket, (aes_gcm, peer_id, _) in list(self.peer.peers.items()):
            if peer_socket != sender_socket:
                try:
                    self.send_encrypted_message(peer_socket, message, aes_gcm)
                except Exception as e:
                    self.peer.message_handler.print_message(
                        format_error_message(f"\r[-] Error sending message para {peer_id}: {e}")
                    )
                    peers_to_remove.append(peer_socket)

        for peer_socket in peers_to_remove:
            self.peer.remove_peer(peer_socket)

    def exchange_peer_info(self, peer_socket, aes_gcm, is_initiator):
        """Exchanges information between peers after establishing connection"""
        try:
            if is_initiator:
                if not self.send_encrypted_message(peer_socket, self.peer.peer_id, aes_gcm):
                    return None
                remote_peer_id = self.receive_encrypted_message(peer_socket, aes_gcm)
            else:
                remote_peer_id = self.receive_encrypted_message(peer_socket, aes_gcm)
                if not self.send_encrypted_message(peer_socket, self.peer.peer_id, aes_gcm):
                    return None

            return remote_peer_id
        except Exception as e:
            self.peer.message_handler.print_message(
                format_error_message(f"[-] Error in ID exchange: {e}")
            )
            return None