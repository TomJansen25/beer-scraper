from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class HiergibtsbierSpider(Spider):
    """Spider to crawl Hier gibt's Bier website"""

    name = "hiergibtsbier"
    main_url = "https://www.hier-gibts-bier.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/bockbier/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/dunkles-bier/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/helles-lagerbier/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/kellerbier/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/pils/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/rauchbier/",
            "https://www.hier-gibts-bier.de/de/bier-aus-franken/weissbier/",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.xpath('//div[@class="product--box box--basic"]')
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                name = product.xpath(".//a[@class='product--title']/@title").get()
                # Skip this beer if it is a package
                if not name or "paket" in name.lower():
                    continue

                availability = product.xpath(
                    ".//button[@class='buybox--button btn is--disabled']"
                ).get()
                available = not bool(availability)

                style = response.url.replace("https://www.hier-gibts-bier.de/de/bier-aus-franken/", "").split("/")[0].replace("-", " ").title()

                loader.add_value("vendor", self.name)
                loader.add_value("style", style)

                loader.add_value("name", name)
                loader.add_xpath(
                    "description", ".//div[@class='product--description']/text()"
                )
                loader.add_value("available", available)

                loader.add_xpath("product_url", './/a[@class="product--image"]/@href')
                loader.add_xpath("image_url", ".//span[@class='image--media']/img/@src")
                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath(
                    "price_eur", ".//a[@class='product--title']/@data-product-price"
                )
                loader.add_xpath(
                    "volume_liter", ".//div[@class='price--unit']/span[2]/text()"
                )
                loader.add_xpath("price_eur_per_liter", ".//div[@class='price--unit']/span[3]/text()")

                loader.add_value("on_sale", False)
                loader.add_value("discount", None)

                yield loader.load_item()
                # logger.info(loader.item.__dict__)
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")
        
        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} "
            f"out of {num_products} products!"
        )

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath(".//a[@class='paging--link paging--next' and @title='Nächste Seite']/@href").get()
        if next_page is not None:
            next_page = f"{self.main_url[:-1]}{next_page}"
            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
