"""Limitation des tentatives de connexion (cache partagé Redis en production)."""
import hashlib

from django.conf import settings
from django.core.cache import cache


def client_ip(request):
    # nginx (sur l'hôte) transmet l'IP réelle ; Gunicorn n'est joignable que via 127.0.0.1
    forwarded = request.META.get("HTTP_X_REAL_IP") or request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")) or "unknown"


def _keys(request, username):
    ip = client_ip(request)
    user_hash = hashlib.sha256((username or "").strip().lower().encode()).hexdigest()[:16]
    return f"login-fail:ip:{ip}", f"login-fail:user:{user_hash}"


def is_locked(request, username):
    limit = settings.LOGIN_MAX_ATTEMPTS
    return any((cache.get(k) or 0) >= limit for k in _keys(request, username))


def register_failure(request, username):
    for key in _keys(request, username):
        if cache.add(key, 1, settings.LOGIN_LOCKOUT_SECONDS):
            continue
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, settings.LOGIN_LOCKOUT_SECONDS)


def reset(request, username):
    cache.delete_many(list(_keys(request, username)))
