from scrapy import Spider, Request
from datetime import datetime
from loguru import logger

from beerspider.items import ProductItemLoader


class RatsherrnSpider(Spider):
    """Spider to crawl Ratsherrn beers sold directly through the Ratsherrn website"""

    name = "ratsherrn"
    main_url = "https://shop.ratsherrn.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://shop.ratsherrn.de/klassik-linie/",
            "https://shop.ratsherrn.de/organic-linie/",
            "https://shop.ratsherrn.de/kenner-linie/",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.product--box")
        logger.info(
            f"Found {len(products)} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                images = product.xpath(
                    ".//span[@class='image--media']//img/@srcset"
                ).get()
                image_url = images.split(", ")[0] if images else None

                loader.add_value("vendor", self.name)
                loader.add_value("brewery", self.name)

                loader.add_xpath(
                    "product_url", ".//div[@class='product--info']//a/@href"
                )
                loader.add_value("image_url", image_url)
                loader.add_value("scraped_from_url", response.url)

                loader.add_css("name", "a.product--title::attr(title)")
                loader.add_css("description", "div.product--description::text")
                loader.add_value("available", True)

                loader.add_xpath(
                    "price_eur", ".//div[@class='product--price']//span/text()"
                )
                price_volume = product.xpath(
                    ".//div[@class='price--unit']//span/text()"
                ).getall()
                loader.add_value("volume_liter", price_volume[1])
                loader.add_value("price_eur_per_liter", price_volume[2])

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} products!"
        )
