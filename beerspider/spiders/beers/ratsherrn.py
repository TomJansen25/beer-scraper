from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class RatsherrnSpider(Spider):
    """Spider to crawl Ratsherrn beers sold directly through the Ratsherrn website"""

    name = "ratsherrn"
    main_url = "https://www.ratsherrn.shop/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = ["https://www.ratsherrn.shop/einzelflaschen"]

        for url in urls:
            yield Request(url=f"{url}?af=50", callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.product-cell__wrapper")
        logger.info(
            f"Found {len(products)} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                images = product.xpath(
                    ".//img[contains(@class, 'mediabox-img')]/@data-srcset"
                ).get()
                if images:
                    images = images.split(", ")
                    images = [img.split(" ")[0] for img in images]
                    image_url = images[-1]
                else:
                    image_url = None

                if (
                    product.xpath(
                        ".//button[contains(@class, 'product-cell__add-to-basket-button btn')]/@title"
                    ).get()
                    == "In den Warenkorb"
                ):
                    availability = True
                else:
                    availability = False

                loader.add_value("vendor", self.name)
                loader.add_value("brewery", self.name)

                product_url = product.xpath(
                    ".//div[contains(@class, 'product-cell__title title')]//a/@href"
                ).get()
                product_url = f"{self.main_url}{product_url}"

                loader.add_value("product_url", product_url)
                loader.add_value("image_url", image_url)
                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath(
                    "name",
                    ".//div[contains(@class, 'product-cell__title title')]//a/text()",
                )
                loader.add_value("available", availability)

                loader.add_xpath("price_eur", ".//strong[@class='price ']//span/text()")
                loader.add_xpath(
                    "price_eur_per_liter",
                    ".//div[@class='base-price base-price--productlist']//span/text()",
                )

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} products!"
        )
