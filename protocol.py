"""
Network protocol for client-server communication
"""

import json
import struct


class Message:
    """Represents a network message"""

    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data or {}

    def to_json(self):
        """Convert message to JSON string"""
        return json.dumps({
            'type': self.type,
            'data': self.data
        })

    @staticmethod
    def from_json(json_str):
        """Create message from JSON string"""
        try:
            obj = json.loads(json_str)
            return Message(obj['type'], obj.get('data', {}))
        except (json.JSONDecodeError, KeyError):
            return None


def send_message(sock, message):
    """
    Send a length-prefixed message over socket

    Args:
        sock: Socket to send on
        message: Message object to send

    Returns:
        True if successful, False otherwise
    """
    try:
        msg_json = message.to_json()
        msg_bytes = msg_json.encode('utf-8')
        # Send length prefix (4 bytes) followed by message
        length = struct.pack('!I', len(msg_bytes))
        sock.sendall(length + msg_bytes)
        return True
    except Exception:
        return False


def receive_message(sock):
    """
    Receive a length-prefixed message from socket

    Args:
        sock: Socket to receive from

    Returns:
        Message object or None if error/disconnect
    """
    try:
        # Read length prefix (4 bytes)
        length_bytes = sock.recv(4)
        if not length_bytes or len(length_bytes) < 4:
            return None

        length = struct.unpack('!I', length_bytes)[0]

        # Read message data
        chunks = []
        bytes_received = 0
        while bytes_received < length:
            chunk = sock.recv(min(length - bytes_received, 4096))
            if not chunk:
                return None
            chunks.append(chunk)
            bytes_received += len(chunk)

        msg_json = b''.join(chunks).decode('utf-8')
        return Message.from_json(msg_json)
    except Exception:
        return None


def set_socket_timeout(sock, timeout):
    """Set socket timeout in seconds"""
    sock.settimeout(timeout)
