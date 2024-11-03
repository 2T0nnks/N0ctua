#!/usr/bin/env python3

import sys
from src.peer import SecurePeer  # Direct class import

def main():
    print("Starting N0ctua...")  # Debug
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
                    print("[-] Invalid port")
                    return

    print(f"Creating peer with id={peer_id}, port={listen_port}")  # Debug
    peer = SecurePeer(listen_port=listen_port, peer_id=peer_id)

    try:
        print("Starting peer...")  # Debug
        peer.start()
    except Exception as e:
        print(f"[-] Error starting peer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()