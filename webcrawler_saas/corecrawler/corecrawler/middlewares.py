from scrapy.exceptions import IgnoreRequest

from netguard import BlockedURL, check_url


class SSRFGuardMiddleware:
    """
    Refuse toute requête vers une cible non publique.
    Placé très tôt : s'applique aussi aux redirections (re-planifiées par
    Scrapy) et aux requêtes robots.txt.
    """

    def __init__(self, allowed_ports):
        self.allowed_ports = allowed_ports

    @classmethod
    def from_crawler(cls, crawler):
        raw = crawler.settings.get("WC_ALLOWED_PORTS", "80,443,8080,8443")
        ports = {int(p) for p in str(raw).split(",") if p.strip()}
        return cls(ports)

    def process_request(self, request, spider=None):
        try:
            # resolve=False : la résolution est contrôlée par SafeResolver au
            # moment de la connexion ; ici on bloque schéma, port, IP littérales.
            check_url(request.url, allowed_ports=self.allowed_ports, resolve=False)
        except BlockedURL as exc:
            raise IgnoreRequest(f"wc-blocked: {exc}") from exc
        return None
