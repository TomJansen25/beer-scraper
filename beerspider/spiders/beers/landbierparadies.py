from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader
from beerspider.settings import NAME_CONTAINS_EXCLUDE


class Landbierparadies(Spider):
    """
    The Landbierparadies spider used to crawl beers from landbierparadies24.de
    """

    name = "landbierparadies"
    allowed_domains = ["landbierparadies24.de"]
    main_url = "https://landbierparadies24.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = ["https://www.landbierparadies24.de/Biere/Helle-Biere/"]

        urls = [f"{url}?_artperpage=100" for url in urls]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.xpath("//div[contains(@class, 'productData')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                loader.add_xpath("description", ".//div[@class='shortdesc']/text()")

                loader.add_xpath(
                    "product_url", ".//div[contains(@class, 'picture')]//a/@href"
                )
                loader.add_xpath(
                    "image_url", ".//img[@class='img-responsive']/@data-src"
                )

                loader.load_item()
                logger.info(loader.item.__dict__)
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")
