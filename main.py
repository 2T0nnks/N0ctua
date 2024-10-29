#!/usr/bin/env python3


import sys
from src.peer import SecurePeer  # Importação direta da classe

def main():
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
                    print("[-] Porta inválida")
                    return

    # Cria e inicia o peer
    peer = SecurePeer(listen_port=listen_port, peer_id=peer_id)

    try:
        peer.start()
    except Exception as e:
        print(f"[-] Erro ao iniciar o peer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()