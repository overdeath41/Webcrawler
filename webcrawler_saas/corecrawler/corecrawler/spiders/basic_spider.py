import scrapy
import json
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError


class BasicSpider(scrapy.Spider):
    name = 'basic_spider'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES': 2,
        'DOWNLOAD_TIMEOUT': 30,
        'USER_AGENT': 'WebCrawler-SaaS/1.0 (Educational Purpose; +https://votresite.com/bot)',
    }
    
    def __init__(self, urls=None, *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        
        # Parser les URLs depuis l'argument
        if urls:
            try:
                # Si c'est une chaîne JSON
                if isinstance(urls, str):
                    self.start_urls = json.loads(urls)
                else:
                    self.start_urls = urls
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, traiter comme une liste séparée par des virgules
                self.start_urls = [url.strip() for url in urls.split(',') if url.strip()]
        else:
            self.start_urls = []
        
        self.logger.info(f"Spider initialisé avec {len(self.start_urls)} URLs")
    
    def start_requests(self):
        """Génère les requêtes initiales"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.errback_httpbin,
                dont_filter=True
            )
    
    def parse(self, response):
        """Parse la réponse et extrait les données"""
        self.logger.info(f"Crawling: {response.url}")
        
        # Extraire les données de base
        item = {
            'url': response.url,
            'title': response.css('title::text').get('').strip(),
            'status_code': response.status,
            'content_length': len(response.body),
        }
        
        # Essayer d'extraire des prix (e-commerce)
        prices = response.css('.price::text, [class*="price"]::text').getall()
        if prices:
            item['prices'] = ', '.join([p.strip() for p in prices if p.strip()])
        
        # Essayer d'extraire des descriptions
        descriptions = response.css('meta[name="description"]::attr(content)').get()
        if descriptions:
            item['description'] = descriptions.strip()
        
        # Extraire les headings H1
        h1_texts = response.css('h1::text').getall()
        if h1_texts:
            item['h1'] = ' | '.join([h.strip() for h in h1_texts if h.strip()])
        
        # Compter les liens
        links = response.css('a::attr(href)').getall()
        item['links_count'] = len(links)
        
        yield item
    
    def errback_httpbin(self, failure):
        """Gère les erreurs de crawl"""
        self.logger.error(f"Erreur de crawl: {failure.request.url}")
        
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}: {response.status}')
            
            yield {
                'url': response.url,
                'status_code': response.status,
                'error': f'HTTP Error {response.status}',
            }
        
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error(f'DNSLookupError on {request.url}')
            
            yield {
                'url': request.url,
                'error': 'DNS Lookup Error',
            }
        
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error(f'TimeoutError on {request.url}')
            
            yield {
                'url': request.url,
                'error': 'Timeout Error',
            }