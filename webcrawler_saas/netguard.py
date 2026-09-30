"""
Garde-fou réseau (anti-SSRF) partagé entre Django et Scrapy.

Module volontairement sans dépendance à Django : le sous-processus Scrapy
l'importe aussi (PYTHONPATH pointe sur ce dossier).

Règle : une URL soumise ne doit JAMAIS permettre d'atteindre une adresse
non publique (boucle locale, réseau privé, lien local, métadonnées cloud,
CGNAT, multicast, réservé...). Sans ce filtre, n'importe quel utilisateur
pourrait faire crawler Redis, PostgreSQL ou l'interface de la box par le
serveur lui-même.
"""
import ipaddress
import os
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = {"http", "https"}
DEFAULT_ALLOWED_PORTS = {80, 443, 8080, 8443}


class BlockedURL(ValueError):
    """URL refusée ; le message est affichable tel quel à l'utilisateur."""


def private_targets_allowed() -> bool:
    """Échappatoire réservée au développement (jamais en production)."""
    return os.getenv("ALLOW_PRIVATE_TARGETS", "False").lower() in {"1", "true", "yes"}


def is_public_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip.split("%", 1)[0])
    except ValueError:
        return False
    # ::ffff:127.0.0.1 et consorts : on juge l'IPv4 encapsulée
    if isinstance(addr, ipaddress.IPv6Address):
        if addr.ipv4_mapped is not None:
            addr = addr.ipv4_mapped
        elif addr.sixtofour is not None:
            addr = addr.sixtofour
    return addr.is_global and not addr.is_multicast


def resolve_host(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError) as exc:
        raise BlockedURL(f"Nom de domaine introuvable : {host}") from exc
    return sorted({info[4][0] for info in infos})


def check_url(url: str, allowed_ports=None, resolve: bool = True) -> str:
    """Lève BlockedURL si l'URL n'est pas crawlable. Renvoie l'URL nettoyée."""
    url = url.strip()
    parts = urlsplit(url)
    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise BlockedURL(f"Seuls http:// et https:// sont acceptés : {url}")
    if not parts.hostname:
        raise BlockedURL(f"Adresse sans nom de domaine : {url}")
    if parts.username or parts.password:
        raise BlockedURL(f"Les identifiants dans l'URL sont interdits : {url}")

    try:
        port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
    except ValueError as exc:
        raise BlockedURL(f"Port invalide : {url}") from exc

    if private_targets_allowed():
        return url

    ports = allowed_ports or DEFAULT_ALLOWED_PORTS
    if port not in ports:
        raise BlockedURL(
            f"Port {port} non autorisé (ports acceptés : "
            f"{', '.join(str(p) for p in sorted(ports))}) : {url}"
        )

    host = parts.hostname
    try:
        ipaddress.ip_address(host)
        candidates = [host]
    except ValueError:
        if host.lower() == "localhost" or host.lower().endswith(".localhost"):
            raise BlockedURL(f"Adresse locale interdite : {url}")
        candidates = resolve_host(host) if resolve else []

    for ip in candidates:
        if not is_public_ip(ip):
            raise BlockedURL(f"Adresse interne ou privée interdite ({ip}) : {url}")
    return url
