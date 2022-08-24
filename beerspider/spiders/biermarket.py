from scrapy import Request, Spider
from loguru import logger

from beerspider.items import ProductItemLoader


class BiermarketSpider(Spider):
    """
    The Bierothek Spider used to crawl Beers from biermarket.de
    """

    name = "Biermarket"
    allowed_domains = ["biermarket.de"]
    main_url = "https://www.biermarket.de/"

    def start_requests(self):
        urls = [
            "https://www.biermarket.de/bier/",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.product-box")
        logger.info(f"Found {len(products)} products on page, starting to crawl...")
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                name = product.xpath(
                    './/div[@class="webing-product-name"]//a/@title'
                ).get()

                # Check for names to exclude from scraping
                if any(
                    n in name.lower()
                    for n in ["paket", "package", "box", "überraschungsbier"]
                ):
                    continue

                # Check whether the product is available and can be ordered
                not_available = product.xpath(
                    './/button[contains(@class, "webing-do-nothing")]'
                ).get()
                available = not bool(not_available)

                sale = product.xpath('.//div[contains(@class, "badge-discount")]').get()
                on_sale = bool(sale)

                if on_sale:
                    sale = product.xpath(
                        './/span[@class="product-detail-list-price-wrapper"]//span/text()'
                    ).getall()
                    original_price, discount = sale
                else:
                    original_price, discount = None, None

                loader.add_value("vendor", self.name)
                loader.add_xpath(
                    "style",
                    './/div[@class="webing-detail-info-nonvariant"]//span/@title',
                )

                loader.add_xpath(
                    "product_url", './/div[@class="product-image-wrapper"]//a/@href'
                )
                loader.add_value("image_url", "")

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                volume = (
                    products[4]
                    .xpath('.//div[@class="webing-detail-info-nonvariant"]/text()')
                    .getall()
                )

                loader.add_xpath("price_eur", './/p[@class="product-price"]/text()')
                loader.add_value("volume_liter", volume[-1])
                loader.add_xpath(
                    "price_eur_per_liter",
                    './/span[@class="price-unit-reference"]/text()',
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)
                loader.add_value("discount", discount)

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} products!"
        )
        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath('.//li[@class="page-item page-next"]').get()
        if next_page is not None:
            next_page_number = response.xpath(
                './/li[@class="page-item page-next"]//input/@value'
            ).get()
            next_page = (
                f"https://www.biermarket.de/bier/?order=topseller&p={next_page_number}"
            )

            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
