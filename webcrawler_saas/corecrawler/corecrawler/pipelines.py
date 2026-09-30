import re
from datetime import datetime, timezone

from itemadapter import ItemAdapter

WS_RE = re.compile(r"\s+")
PRICE_RE = re.compile(r"\d[\d\s\u00a0\u202f.,]*")
CURRENCY_RE = re.compile(r"[€$£¥]|EUR|USD|GBP|CHF", re.IGNORECASE)


class CleanTextPipeline:
    """Normalise les espaces et horodate chaque ligne."""

    TEXT_FIELDS = ("title", "description", "h1", "error")

    def process_item(self, item, spider=None):
        adapter = ItemAdapter(item)
        adapter.setdefault("crawled_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        for field in self.TEXT_FIELDS:
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = WS_RE.sub(" ", value).strip()
        return item


class PriceCleaningPipeline:
    """Standardise les prix détectés : « 1 299,00 € » -> « 1299.00 € »."""

    def process_item(self, item, spider=None):
        adapter = ItemAdapter(item)
        prices = adapter.get("prices")
        if prices:
            cleaned = [self.clean(p) for p in prices.split(" | ")]
            adapter["prices"] = " | ".join(dict.fromkeys(p for p in cleaned if p))
        return item

    @staticmethod
    def clean(raw):
        raw = raw.strip()
        match = PRICE_RE.search(raw)
        if not match:
            return ""
        number = re.sub(r"[\s\u00a0\u202f]", "", match.group()).rstrip(".,")
        # 1.299,00 -> 1299.00 ; 1,299.00 -> 1299.00 ; 12,50 -> 12.50
        if "," in number and "." in number:
            if number.rfind(",") > number.rfind("."):
                number = number.replace(".", "").replace(",", ".")
            else:
                number = number.replace(",", "")
        elif "," in number:
            number = number.replace(",", ".")
        currency = CURRENCY_RE.search(raw)
        return f"{number} {currency.group().upper() if currency else ''}".strip()
