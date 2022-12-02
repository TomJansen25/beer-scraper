from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class BierothekSpider(Spider):
    """
    The Bierothek Spider used to crawl Beers from bierothek.de
    """

    name = "bierothek"
    allowed_domains = ["bierothek.de"]
    main_url = "https://bierothek.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://bierothek.de/bierstile/ale/",
            "https://bierothek.de/bierstile/alkoholfreie-biere",
            "https://bierothek.de/bierstile/barley-wine",
            "https://bierothek.de/bierstile/belgische-bierstile",
            "https://bierothek.de/bierstile/bio-biere-nach-de-oeko006",
            "https://bierothek.de/bierstile/bockbiere",
            "https://bierothek.de/bierstile/fassgereifte-biere",
            "https://bierothek.de/bierstile/fraenkische-biere",
            "https://bierothek.de/bierstile/frucht-sauerbiere",
            "https://bierothek.de/bierstile/glutenfreie-biere",
            "https://bierothek.de/bierstile/india-pale-ale",
            "https://bierothek.de/bierstile/lager",
            "https://bierothek.de/bierstile/pale-ale",
            "https://bierothek.de/bierstile/pils",
            "https://bierothek.de/bierstile/porter-stout",
            "https://bierothek.de/bierstile/rauchbiere",
            "https://bierothek.de/bierstile/weitere-stile",
            "https://bierothek.de/bierstile/weizen",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.article_entry")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                name = product.xpath('.//div[@class="title"]/text()').get()
                if any(n in name.lower() for n in ["paket", "package", "box"]):
                    continue

                not_available = product.xpath(
                    './/div[contains(@class, "out-of-stock")]'
                ).get()
                available = not bool(not_available)

                product_url = product.xpath(
                    './/div[contains(@class, "product-item")]//a/@href'
                ).get()
                image_url = product.xpath(
                    './/div[contains(@class, "img")]/@data-src'
                ).get()
                image_url = image_url.replace("url('", "").replace("')", "")

                prices = product.xpath('.//div[@class="meta"]/text()').getall()
                prices = prices[1].replace("\t", "").replace("\n", "")
                volume, price_per_liter = prices.split("—")

                if any(n in volume.lower() for n in ["1 st.", "g"]):
                    continue

                sale = product.xpath('.//span[@class="ribbon red"]//small/text()').get()
                on_sale = bool(sale)

                style = response.url.split("/")[-1].replace("-", " ").title()

                loader.add_value("vendor", self.name)
                loader.add_xpath(
                    "brewery", './/div[@class="meta"]//a[@class="smooth"]/text()'
                )
                loader.add_value("style", style)

                loader.add_value("product_url", f"{self.main_url[:-1]}{product_url}")
                loader.add_value("image_url", f"{self.main_url[:-1]}{image_url}")

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_xpath("price_eur", './/div[@class="price"]//span/text()')
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value("on_sale", on_sale)
                loader.add_xpath(
                    "original_price",
                    './/div[contains(@class, "original-price")]/text()',
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
