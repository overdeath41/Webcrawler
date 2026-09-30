import json
from pathlib import Path

import scrapy
from scrapy.exceptions import IgnoreRequest
from scrapy.http import TextResponse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import (
    ConnectionRefusedError, DNSLookupError, TCPTimedOutError, TimeoutError,
)

PROGRESS = "[wc-progress]"
MAX_PRICES = 10


class BasicSpider(scrapy.Spider):
    """Visite chaque URL fournie (sans suivre les liens) et extrait les infos clés."""

    name = "basic_spider"

    def __init__(self, urls_file=None, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if urls_file:
            self.start_urls = json.loads(Path(urls_file).read_text(encoding="utf-8"))
        elif urls:
            try:
                self.start_urls = json.loads(urls)
            except json.JSONDecodeError:
                self.start_urls = [u.strip() for u in urls.split(",") if u.strip()]
        else:
            self.start_urls = []
        self.logger.info("Spider initialisé avec %d URL(s)", len(self.start_urls))

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, callback=self.parse, errback=self.on_error,
                dont_filter=True, cb_kwargs={"requested_url": url},
            )

    # ------------------------------------------------------------------ succès
    def parse(self, response, requested_url):
        item = {
            "url": requested_url,
            "status_code": response.status,
            "content_length": len(response.body),
        }
        if response.url != requested_url:
            item["error"] = f"Redirigé vers {response.url}"

        if isinstance(response, TextResponse):
            item["title"] = (response.css("title::text").get() or "").strip()
            item["description"] = (
                response.css('meta[name="description"]::attr(content)').get()
                or response.css('meta[property="og:description"]::attr(content)').get()
                or ""
            ).strip()
            h1 = [" ".join(t.split()) for t in response.css("h1 ::text").getall()]
            item["h1"] = " | ".join(t for t in h1 if t)
            item["prices"] = self.extract_prices(response)
            item["links_count"] = len(response.css("a::attr(href)").getall())
        else:
            ctype = response.headers.get("Content-Type", b"").decode(errors="replace")
            item["error"] = f"Contenu non HTML ({ctype or 'type inconnu'})"

        self.progress("ok", requested_url)
        yield item

    @staticmethod
    def extract_prices(response):
        found = []
        # Données structurées d'abord (fiables), puis heuristique CSS
        found += response.css('[itemprop="price"]::attr(content)').getall()
        found += response.css('meta[property="product:price:amount"]::attr(content)').getall()
        found += [p for p in response.css('.price ::text, [class*="price"] ::text').getall() if any(c.isdigit() for c in p)]
        cleaned = [p.strip() for p in found if p and p.strip()]
        return " | ".join(list(dict.fromkeys(cleaned))[:MAX_PRICES])

    # ------------------------------------------------------------------ échecs
    def on_error(self, failure):
        request = failure.request
        url = request.cb_kwargs.get("requested_url", request.url)
        item = {"url": url}
        message = str(failure.value)

        if failure.check(HttpError):
            item["status_code"] = failure.value.response.status
            item["error"] = f"Erreur HTTP {failure.value.response.status}"
        elif "wc-blocked" in message:
            item["error"] = "Bloqué : adresse interne ou privée"
        elif failure.check(IgnoreRequest) and "robots.txt" in message:
            item["error"] = "Interdit par le robots.txt du site"
        elif failure.check(DNSLookupError):
            item["error"] = "Nom de domaine introuvable"
        elif failure.check(TimeoutError, TCPTimedOutError):
            item["error"] = "Délai dépassé"
        elif failure.check(ConnectionRefusedError):
            item["error"] = "Connexion refusée"
        else:
            item["error"] = f"Échec : {failure.type.__name__}"

        self.logger.warning("Échec %s : %s", url, item["error"])
        self.progress("fail", url)
        yield item

    def progress(self, state, url):
        # Ligne lue en direct par crawler/tasks.py pour la jauge de progression
        self.logger.info("%s %s %s", PROGRESS, state, url)
