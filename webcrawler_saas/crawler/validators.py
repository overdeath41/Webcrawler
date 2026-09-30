from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from netguard import BlockedURL, check_url

from .models import parse_urls

_url_syntax = URLValidator(schemes=["http", "https"])


def validate_url_list(raw: str) -> list[str]:
    """
    Valide la saisie d'une mission AVANT toute création en base.
    Renvoie la liste nettoyée ou lève ValidationError (messages en français).
    """
    urls = parse_urls(raw)
    if not urls:
        raise ValidationError("Indiquez au moins une URL.")
    limit = settings.MAX_URLS_PER_TASK
    if len(urls) > limit:
        raise ValidationError(f"{len(urls)} URLs saisies : le maximum est de {limit} par mission.")

    errors = []
    for url in urls:
        try:
            _url_syntax(url)
        except ValidationError:
            errors.append(f"URL mal formée : {url}")
            continue
        try:
            check_url(url, allowed_ports=settings.ALLOWED_TARGET_PORTS)
        except BlockedURL as exc:
            errors.append(str(exc))
    if errors:
        raise ValidationError(errors)
    return urls
