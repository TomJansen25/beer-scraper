from scrapy import Spider, Request
from loguru import logger
from scrapy.shell import inspect_response


class BeerwulfSpider(Spider):
    name = "beerwulf"
    allowed_domains = ["beerwulf.com"]
    start_urls = ["https://beerwulf.com/de-de/"]

    def start_requests(self):
        urls = [
            "https://www.beerwulf.com/de-de/c/alle-biere"
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse, meta=dict(playwright=True))

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        inspect_response(response, self)

        products = response.css("div.article_entry")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0


