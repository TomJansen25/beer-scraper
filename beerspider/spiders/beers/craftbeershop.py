from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader


class CraftbeerShopSpider(Spider):
    """
    Craftbeer Shop Spider Class
    """

    name = "craftbeer_shop"
    allowed_domains = ["craftbeer-shop.com"]
    main_url = "https://www.craftbeer-shop.com/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://www.craftbeer-shop.com/abteibier",
            "https://www.craftbeer-shop.com/ale",
            "https://www.craftbeer-shop.com/alkoholfrei",
            "https://www.craftbeer-shop.com/barley-wine",
            "https://www.craftbeer-shop.com/barrel-aged",
            "https://www.craftbeer-shop.com/bierspezialitaeten",
            "https://www.craftbeer-shop.com/bio-bier",
            "https://www.craftbeer-shop.com/bockbier",
            "https://www.craftbeer-shop.com/cider",
            "https://www.craftbeer-shop.com/glutenfrei",
            "https://www.craftbeer-shop.com/gose",
            "https://www.craftbeer-shop.com/hard-seltzer",
            "https://www.craftbeer-shop.com/helles",
            "https://www.craftbeer-shop.com/ipa",
            "https://www.craftbeer-shop.com/lager-pilsener",
            "https://www.craftbeer-shop.com/lambic",
            "https://www.craftbeer-shop.com/maerzen",
            "https://www.craftbeer-shop.com/nitro-bier",
            "https://www.craftbeer-shop.com/pale-ale",
            "https://www.craftbeer-shop.com/porter-stout",
            "https://www.craftbeer-shop.com/saison",
            "https://www.craftbeer-shop.com/sauerbier",
            "https://www.craftbeer-shop.com/smokebeer",
            "https://www.craftbeer-shop.com/starkbier",
            "https://www.craftbeer-shop.com/trappistenbier",
            "https://www.craftbeer-shop.com/weizen",
            "https://www.craftbeer-shop.com/witbier",
            "https://www.craftbeer-shop.com/sommerbier",
            "https://www.craftbeer-shop.com/Sonderangebote",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}...")

        products = response.css("div.product-cell__wrapper")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                title = product.xpath(
                    ".//div[contains(@class, 'product-cell__title title')]/a/text()"
                ).get()
                full_name = " ".join(title.split(" ")[:-1])
                volume = title.split(" ")[-1]

                availability = product.xpath(
                    ".//button[contains(@class, 'product-cell__add-to-basket-button')]"
                ).get()
                available = bool(availability)

                discount = product.xpath(
                    './/div[@class="am-discount__label"]//span/text()'
                ).get()
                on_sale = bool(discount)

                # Check whether product has a price range, and if so get the single bottle value
                price_eur = product.xpath(
                    ".//span[contains(@class, 'second-range-price')]/text()"
                ).get()
                price_per_liter = product.xpath(
                    ".//div[contains(@class, 'base-price')]//span/text()"
                ).get()
                if not price_eur:
                    price_eur = product.xpath(
                        ".//div[contains(@class, 'price_wrapper')]//strong//"
                        "meta[@itemprop='price']/@content"
                    ).get()
                else:
                    price_per_liter = price_per_liter.split(" - ")[-1]

                style = (
                    response.url.split("/")[-1].split("_")[0].replace("-", " ").title()
                )

                loader.add_value("brewery", "")
                loader.add_value("name", full_name)
                loader.add_value("available", available)
                loader.add_value("vendor", self.name.replace("_", " "))
                loader.add_value("style", style)
                loader.add_xpath(
                    "product_url", ".//a[contains(@class, 'image-wrapper')]/@href"
                )
                loader.add_xpath(
                    "image_url", ".//img[contains(@class, 'mediabox-img')]/@data-src"
                )
                loader.add_value("scraped_from_url", response.url)
                loader.add_value("description", "")

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value("on_sale", on_sale)
                loader.add_value("discount", discount)

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} "
            f"out of {num_products} products!"
        )

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath("//button[@class='load-more__pagination']/@id").get()
        if next_page is not None:
            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
