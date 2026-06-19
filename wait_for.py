"""Attend qu'un service TCP (db, redis) soit joignable avant de continuer."""
import socket
import sys
import time

host, port = sys.argv[1], int(sys.argv[2])
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"{host}:{port} est prêt")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"Timeout: {host}:{port} injoignable après 60s", file=sys.stderr)
sys.exit(1)
