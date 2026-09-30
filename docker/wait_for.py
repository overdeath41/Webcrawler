"""Attend qu'un service TCP (db, redis) soit joignable avant de continuer."""
import socket
import sys
import time

host, port = sys.argv[1], int(sys.argv[2])
deadline = time.time() + int(sys.argv[3]) if len(sys.argv) > 3 else time.time() + 90
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"{host}:{port} est prêt")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"Timeout: {host}:{port} injoignable", file=sys.stderr)
sys.exit(1)
