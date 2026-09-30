# Réglages Scrapy — WebCrawler SaaS
# Les valeurs dépendantes de l'instance (délai, User-Agent, fichier de sortie)
# sont passées en ligne de commande par crawler/tasks.py.
BOT_NAME = "corecrawler"
SPIDER_MODULES = ["corecrawler.spiders"]
NEWSPIDER_MODULE = "corecrawler.spiders"

# Robot identifiable et poli
USER_AGENT = "WebCrawler-SaaS/1.1 (+crawler respectueux de robots.txt)"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.6",
}

# --- Anti-SSRF (défense en profondeur) ---------------------------------------
# 1) le middleware refuse toute requête (y compris redirections et robots.txt)
#    vers une IP littérale non publique ;
# 2) le résolveur DNS refuse les noms qui résolvent vers une IP non publique,
#    au moment même de la connexion (pas de contournement par DNS rebinding).
DOWNLOADER_MIDDLEWARES = {
    "corecrawler.middlewares.SSRFGuardMiddleware": 50,
}
DNS_RESOLVER = "corecrawler.resolver.SafeResolver"
WC_ALLOWED_PORTS = "80,443,8080,8443"

ITEM_PIPELINES = {
    "corecrawler.pipelines.CleanTextPipeline": 300,
    "corecrawler.pipelines.PriceCleaningPipeline": 400,
}

# Robustesse
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
DOWNLOAD_TIMEOUT = 30
DOWNLOAD_MAXSIZE = 10 * 1024 * 1024      # 10 Mo par page, pas plus
DOWNLOAD_WARNSIZE = 2 * 1024 * 1024
REDIRECT_MAX_TIMES = 5
DEPTH_LIMIT = 1                           # on ne suit pas les liens

HTTPCACHE_ENABLED = False
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
