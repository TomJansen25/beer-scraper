from loguru import logger
from datetime import datetime
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class HolyCraftSpider(Spider):
    """
    The Holy Craft Spider used to crawl Beers from holycraft.de
    """

    name = "holycraft"
    allowed_domains = ["holycraft.de"]
    main_url = "https://holycraft.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://holycraft.de/Weizen",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.xpath("//div[contains(@class, 'product-wrapper')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                loader.add_value("vendor", self.name)
                loader.add_xpath(
                    "brewery",
                )
                loader.add_value(
                    "style",
                )

                loader.add_value("product_url", f"{self.main_url[:-1]}{product_url}")
                loader.add_value("image_url", f"{self.main_url[:-1]}{image_url}")

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_xpath(
                    "price_eur",
                )
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value(
                    "on_sale",
                )
                loader.add_xpath(
                    "original_price",
                )

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} "
            f"out of {num_products} products!"
        )
