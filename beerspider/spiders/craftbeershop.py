import scrapy
from loguru import logger

from beerspider.items import ProductItemLoader


class CraftbeerShopSpider(scrapy.Spider):
    """
    Craftbeer Shop Spider Class
    """

    name = "Craftbeer Shop"
    allowed_domains = ["craftbeer-shop.com"]
    main_url = "https://www.craftbeer-shop.com/"

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
            "https://www.craftbeer-shop.com/Sale",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        page = response.url.split("/")[-1]
        logger.info(f"Crawling {response.url}...")

        products = response.css("div.product-cell__wrapper")
        logger.info(f"Found {len(products)} products on page {response.url}, starting to crawl...")
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                title = (
                    product.css("div.product-cell__title-wrapper")
                    .css("h4.product-cell__title")
                    .css("a::text")
                    .get()
                )
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

                loader.add_value("brewery", "")
                loader.add_value("name", full_name)
                loader.add_value("available", available)
                loader.add_value("vendor", self.name)
                loader.add_value("style", page)
                loader.add_xpath(
                    "image_url", './/div[@class="image-content"]//meta/@content'
                )
                loader.add_xpath(
                    "product_url",
                    './/div[@class="product-cell__caption caption text-center"]//meta/@content',
                )
                loader.add_value("scraped_from_url", response.url)
                loader.add_value("description", "")
                loader.add_css("price_eur", "div.price_wrapper > strong > span::text")
                loader.add_value("volume_liter", volume)
                loader.add_css("price_eur_per_liter", "div.base_price > span::text")
                loader.add_value("on_sale", on_sale)
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
        next_page = response.css("li.next > a").attrib.get("href")
        if next_page is not None:
            print(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
