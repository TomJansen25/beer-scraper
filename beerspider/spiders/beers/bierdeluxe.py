from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class BierDeluxeSpider(Spider):
    name = "bier_deluxe"
    allowed_domains = ["bier-deluxe.de"]
    main_url = "https://www.bier-deluxe.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = ["https://www.bier-deluxe.de/sortiment/"]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}...")

        products = response.xpath("//div[contains(@class, 'product--box')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                not_available = bool(
                    product.xpath(".//div[@class='bdlnotavailable']").get()
                )
                available = not not_available

                style = product.xpath(".//div[@class='hphighlightinfo']/text()").get()

                loader.add_xpath("name", ".//a[@class='product--image']/@title")
                loader.add_value("vendor", self.name.replace("_", " "))
                loader.add_xpath(
                    "description",
                    ".//div[contains(@class, 'bdlshortdescription')]/text()",
                )

                loader.add_value("style", style.replace("Bierstil:", ""))

                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath("product_url", ".//a[@class='product--image']/@href")

                image_urls = product.xpath(
                    ".//span[@class='image--media']//img/@srcset"
                ).get()
                loader.add_value("image_url", image_urls.split(",")[0])

                original_price = product.xpath(
                    ".//span[@class='price--line-through']/text()"
                ).get()
                price_volume_info = product.xpath(
                    ".//div[contains(@class, 'bdldetailsubinfo')]/text()"
                ).getall()
                if original_price:
                    volume, _, price_eur = price_volume_info[0].split(" | ")
                    price_eur_per_liter = price_volume_info[1].replace(" | ", "")
                else:
                    volume, _, price_eur, price_eur_per_liter = price_volume_info[
                        0
                    ].split(" | ")

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_eur_per_liter)

                loader.add_value("available", available)

                loader.add_value("on_sale", bool(original_price))
                loader.add_value("original_price", original_price)

                loader.load_item()
                logger.info(loader.item.__dict__)
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} "
            f"out of {num_products} products!"
        )

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath(
            "//a[@class='paging--link paging--next' and @title='Nächste Seite']/@href"
        ).get()
        if next_page is not None:
            current_page = int(
                response.xpath(".//a[@class='paging--link is--active']/text()").get()
            )
            if current_page != 1:
                next_page_url = response.url.replace(
                    f"p={current_page}", f"p={current_page + 1}"
                )
            else:
                next_page_url = f"{response.url}?p=2"
            logger.info(f"Found another page, moving to: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)
