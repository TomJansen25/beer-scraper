from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class BierKaufenSpider(Spider):
    name = "bier_kaufen"
    allowed_domains = ["bier-kaufen.de"]
    main_url = "https://www.bier-kaufen.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            # "https://www.bier-kaufen.de/Angebote/",
            "https://www.bier-kaufen.de/Alkoholfreie/",
            "https://www.bier-kaufen.de/Biermix/",
            "https://www.bier-kaufen.de/Bio-Bier/",
            "https://www.bier-kaufen.de/Helles/",
            "https://www.bier-kaufen.de/Keller-Zwickl/",
            "https://www.bier-kaufen.de/Landbier/",
            "https://www.bier-kaufen.de/Leichte-Biere/",
            "https://www.bier-kaufen.de/Pils/",
            "https://www.bier-kaufen.de/Schwarzbiere/",
            "https://www.bier-kaufen.de/Spezial/",
            "https://www.bier-kaufen.de/Weizen/Dunkles-Weizen/",
            "https://www.bier-kaufen.de/Weizen/Hefeweizen/",
            "https://www.bier-kaufen.de/Weizen/Kristallweizen/",
            "https://www.bier-kaufen.de/Weizen/leichtes-Weizen/",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}...")

        products = response.xpath("//div[contains(@class, 'cms-listing-col')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                available = bool(
                    product.xpath(".//button[@class='btn btn-block btn-buy']").get()
                )

                loader.add_xpath("name", ".//a[@class='product-name']/@title")
                loader.add_value("vendor", self.name.replace("_", " "))
                loader.add_xpath(
                    "description", ".//div[@class='product-description']/text()"
                )
                loader.add_value("style", response.url.split("/")[-1])

                loader.add_xpath("product_url", ".//a[@class='product-name']/@href")
                loader.add_xpath(
                    "image_url",
                    ".//a[contains(@class, 'product-image-link')]//img/@src",
                )

                loader.add_value("scraped_from_url", response.url)
                loader.add_value("available", available)

                on_sale = bool(
                    product.xpath(".//div[contains(@class, 'badge-discount')]").get()
                )

                if on_sale:
                    price = product.xpath(
                        ".//span[@class='product-price with-list-price']/text()"
                    ).get()
                    original_price = product.xpath(
                        ".//span[@class='list-price-price']/text()"
                    ).get()
                    discount = product.xpath(
                        ".//span[@class='list-price-percentage']/text()"
                    ).get()
                else:
                    price = product.xpath(
                        ".//span[@class='product-price']/text()"
                    ).get()
                    original_price, discount = None, None

                loader.add_value("price_eur", price)

                loader.add_xpath(
                    "volume_liter", ".//span[@class='price-unit-content']/text()"
                )
                loader.add_xpath(
                    "price_eur_per_liter",
                    ".//span[@class='price-unit-reference']/text()",
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)
                loader.add_value("discount", discount)

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
        next_page = response.xpath("//li[@class='page-item page-next']")
        if next_page.get() is not None:
            next_page_value = next_page.xpath(".//input[@id='p-next']/@value").get()
            base_url = response.url.rsplit("/", 1)[0]
            next_page_url = f"{base_url}/?p={next_page_value}"
            logger.info(f"Found another page, moving to: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)
