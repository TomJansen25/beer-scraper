from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class BiermarketSpider(Spider):
    """
    The Bierothek Spider used to crawl Beers from biermarket.de
    """

    name = "biermarket"
    allowed_domains = ["biermarket.de"]
    main_url = "https://www.biermarket.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            # "https://www.biermarket.de/bier/",
            "https://www.biermarket.de/bier/biersorten/pilsner/",
            "https://www.biermarket.de/bier/biersorten/weizenbier/",
            "https://www.biermarket.de/bier/biersorten/helles/",
            "https://www.biermarket.de/bier/biersorten/export/",
            "https://www.biermarket.de/bier/biersorten/gruenhopfen/",
            "https://www.biermarket.de/bier/biersorten/dunkles/",
            "https://www.biermarket.de/bier/biersorten/schwarzbier/",
            "https://www.biermarket.de/bier/biersorten/lager/",
            "https://www.biermarket.de/bier/biersorten/maerzen/",
            "https://www.biermarket.de/bier/biersorten/ipa/",
            "https://www.biermarket.de/bier/biersorten/bockbier/",
            "https://www.biermarket.de/bier/biersorten/doppelbock/",
            "https://www.biermarket.de/bier/biersorten/eisbock/",
            "https://www.biermarket.de/bier/weissbiere/hefe-weissbier/",
            "https://www.biermarket.de/bier/weissbiere/weissbier-hell/",
            "https://www.biermarket.de/bier/weissbiere/dunkles-weissbier/",
            "https://www.biermarket.de/bier/weissbiere/kristallweizen/",
            "https://www.biermarket.de/bier/weissbiere/weizenbock/",
            "https://www.biermarket.de/bier/weissbiere/weizen-doppelbock/",
            "https://www.biermarket.de/bier/weissbiere/weissbier-leicht/",
            "https://www.biermarket.de/bier/weissbiere/alkoholfreies-weissbier/",
            "https://www.biermarket.de/bier/spezialbiere/bio-bier/",
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

                name = product.xpath('.//a[@class="product-name"]/@title').get()

                # Check for names of products to exclude from scraping
                if any(
                    n in name.lower()
                    for n in ["paket", "package", "box", "überraschungsbier", "senf"]
                ):
                    continue

                # Check whether the product is available and can be ordered
                available = product.xpath('.//form[@class="buy-widget"]').get()
                available = bool(available)

                sale = product.xpath('.//div[contains(@class, "badge-discount")]').get()
                on_sale = bool(sale)

                if on_sale:
                    original_price = product.xpath(
                        './/span[@class="list-price-price"]/text()'
                    ).get()
                    discount = (
                        product.xpath('.//span[@class="list-price-percentage"]/text()')
                        .get()
                        .replace("(", "")
                        .replace("% gespart)", "")
                    )
                    price_eur = product.xpath(
                        './/span[@class="product-price with-list-price"]/text()'
                    ).get()
                else:
                    original_price, discount = None, None
                    price_eur = product.xpath(
                        ".//span[@class='product-price']/text()"
                    ).get()

                loader.add_value("vendor", self.name)
                loader.add_value("style", response.url.split("/")[-2])

                loader.add_xpath("product_url", './/a[@class="product-name"]/@href')
                loader.add_xpath(
                    "image_url", ".//img[contains(@class, 'product-image')]/@src"
                )

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_value("price_eur", price_eur)
                loader.add_xpath(
                    "volume_liter", ".//span[@class='price-unit-content']/text()"
                )
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
