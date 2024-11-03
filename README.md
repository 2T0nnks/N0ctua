# N0ctua Project 
       ,___,
       [O.o]
       /)__)
    ---"---"---


A secure peer-to-peer encrypted chat application built with Python. This tool enables direct communication between peers with end-to-end encryption.

## Updates v1.2

- Session Management System
- Automatic session rotation mechanism
- Session validation for all operations
- Enhanced peer verification
- New Command (sessions) for view and monitor active sessions
- Implemented CommandHandler system
- Fixed connection handling issues








## Features

-  End-to-end encryption using RSA and AES-GCM
-  Peer-to-peer architecture (no central server)
-  Automatic key generation and exchange
-  Direct connection between peers
-  Colored terminal interface
-  Message timestamps
-  Unique peer identification
-  Connection authentication using secrets

## Requirements

- Python 3.6+
- Dependencies:
  ```
  cryptography==41.0.0
  colorama==0.4.6
  ```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/2T0nnks/N0ctua.git
cd N0ctua
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python3 main.py
```

Optional arguments:
- `--id=<peer_id>`: Set a custom peer ID
- `--port=<port_number>`: Set a specific port number

Example:
```bash
python3 peer.py --id=Alice --port=5000
```

2. When the application starts, it will display your connection information:
```
==================== Connection Information ====================
ID: Peer_abc123
Address: 192.168.1.100:5000
Secret: xyw7z9...

Connection string (copy this line):
192.168.1.100:5000:xyw7z9...

Type 'help' to see available commands
=================================================================
```

3. To connect to another peer, use the `connect` or `c` command with their connection string:
```
connect 192.168.1.101:5000:their_secret
```

4. Available commands:
- `connect` or `c`: Connect to another peer
- `sessions`: Display active session information and status
- `help`: Show help message
- `exit`, `quit`, or `sair`: Close the application

## Security Features

- **RSA Key Pair**: Generated on startup for initial key exchange
- **AES-GCM**: Used for symmetric encryption of messages
- **Connection Authentication**: Uses a secret token to verify connections
- **Secure Key Exchange**: Implements secure key exchange protocol
- **No Message Storage**: Messages are only held in memory during transmission
- **Automatic session rotation (every 30 minutes)**
- **Session state monitoring and validation**

## Message Format

Messages are displayed with timestamps and peer IDs:
```
[HH:MM:SS] Peer_abc123: Hello ?
```


## Note on Security

While this tool implements encryption and security measures, it should be used with caution in sensitive environments. Always verify the identity of peers you're connecting to through a separate channel.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. The developers are not responsible for any misuse or damage caused by this application.