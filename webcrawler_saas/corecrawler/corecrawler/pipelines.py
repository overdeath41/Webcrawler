from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.exceptions import DropItem
import re


class CorecrawlerPipeline:
    """Pipeline principal pour nettoyer et valider les données"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Ajouter timestamp si pas présent
        if not adapter.get('crawled_at'):
            adapter['crawled_at'] = datetime.now().isoformat()
        
        # Nettoyer les espaces des textes
        for field in ['title', 'description', 'h1', 'h2']:
            value = adapter.get(field)
            if value:
                if isinstance(value, str):
                    adapter[field] = self._clean_text(value)
                elif isinstance(value, list):
                    adapter[field] = ' | '.join([self._clean_text(v) for v in value])
        
        # Valider l'URL
        url = adapter.get('url')
        if url and not self._is_valid_url(url):
            spider.logger.warning(f"URL invalide: {url}")
        
        return item
    
    def _clean_text(self, text):
        """Nettoie le texte en supprimant les espaces multiples et les caractères spéciaux"""
        if not text:
            return ''
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les espaces au début et à la fin
        text = text.strip()
        return text
    
    def _is_valid_url(self, url):
        """Vérifie si l'URL est valide"""
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...ou ip
            r'(?::\d+)?'  # port optionnel
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class DuplicatesPipeline:
    """Pipeline pour éviter les doublons"""
    
    def __init__(self):
        self.urls_seen = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('url')
        
        if url in self.urls_seen:
            spider.logger.warning(f"URL dupliquée ignorée: {url}")
            raise DropItem(f"URL dupliquée: {url}")
        else:
            self.urls_seen.add(url)
            return item


class PriceCleaningPipeline:
    """Pipeline pour nettoyer et standardiser les prix"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Nettoyer le champ price
        price = adapter.get('price')
        if price:
            adapter['price'] = self._clean_price(price)
        
        # Nettoyer le champ prices (pour les listes de prix)
        prices = adapter.get('prices')
        if prices:
            if isinstance(prices, str):
                prices = [p.strip() for p in prices.split(',')]
            adapter['prices'] = ', '.join([self._clean_price(p) for p in prices if p])
        
        return item
    
    def _clean_price(self, price_str):
        """Extrait et nettoie un prix d'une chaîne"""
        if not price_str:
            return ''
        
        # Supprimer les espaces
        price_str = price_str.strip()
        
        # Extraire les nombres et décimales
        match = re.search(r'[\d\s]+[.,]?\d*', price_str)
        if match:
            price = match.group().replace(' ', '').replace(',', '.')
            # Trouver le symbole de devise
            currency_match = re.search(r'[€$£¥]|EUR|USD|GBP', price_str)
            if currency_match:
                return f"{price} {currency_match.group()}"
            return price
        
        return price_str