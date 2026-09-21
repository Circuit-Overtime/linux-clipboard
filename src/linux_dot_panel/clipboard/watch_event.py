"""Receive one wl-paste --watch event and forward it to the daemon."""

from __future__ import annotations

import base64
import os
import socket
import sys

from linux_dot_panel.clipboard.capture import MAX_TEXT_BYTES
from linux_dot_panel.ipc.protocol import decode_message, encode_message, socket_path


def main() -> int:
    if os.environ.get("CLIPBOARD_STATE") in {"nil", "sensitive"}:
        return 0
    data = sys.stdin.buffer.read(MAX_TEXT_BYTES + 1)
    if not data or len(data) > MAX_TEXT_BYTES:
        return 0
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return 0
    message = encode_message(
        {"command": "clipboard_event", "data": base64.b64encode(data).decode("ascii")}
    )
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(str(socket_path()))
            connection.sendall(message)
            response = bytearray()
            while b"\n" not in response:
                chunk = connection.recv(1024)
                if not chunk:
                    return 1
                response.extend(chunk)
                if len(response) > 4096:
                    return 1
        result = decode_message(bytes(response).split(b"\n", 1)[0])
        return 0 if result.get("ok") is True else 1
    except (OSError, ValueError, TypeError):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
