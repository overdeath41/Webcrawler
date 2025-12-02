import scrapy


class WebPageItem(scrapy.Item):
    """Item pour stocker les données d'une page web"""
    url = scrapy.Field()
    title = scrapy.Field()
    status_code = scrapy.Field()
    content_length = scrapy.Field()
    h1 = scrapy.Field()
    h2 = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    links_count = scrapy.Field()
    images_count = scrapy.Field()
    prices = scrapy.Field()
    crawled_at = scrapy.Field()
    error = scrapy.Field()


class ProductItem(scrapy.Item):
    """Item pour stocker les données de produits e-commerce"""
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    availability = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    brand = scrapy.Field()
    sku = scrapy.Field()
    category = scrapy.Field()
    crawled_at = scrapy.Field()