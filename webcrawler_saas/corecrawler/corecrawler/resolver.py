from scrapy.resolver import CachingThreadedResolver
from twisted.internet.error import DNSLookupError

from netguard import is_public_ip, private_targets_allowed


class SafeResolver(CachingThreadedResolver):
    """Résolveur DNS qui refuse les adresses non publiques (anti-SSRF / DNS rebinding)."""

    def getHostByName(self, name, timeout=None):
        d = super().getHostByName(name, timeout)
        d.addCallback(self._check, name)
        return d

    @staticmethod
    def _check(ip, name):
        if not private_targets_allowed() and not is_public_ip(ip):
            raise DNSLookupError(f"wc-blocked: {name} résout vers une adresse interne ({ip})")
        return ip
