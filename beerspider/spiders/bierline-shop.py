from loguru import logger
from scrapy import Request, Selector, Spider
from scrapy.shell import inspect_response

from beerspider.items import ProductItemLoader


class BierlineSpider(Spider):
    name = "Bierlinie"
    main_url = "https://www.bierlinie-shop.de/"

    def start_requests(self):
        urls = [
            "https://www.bierlinie-shop.de/biersorten/abteibier",
            "https://www.bierlinie-shop.de/biersorten/ale",
            "https://www.bierlinie-shop.de/biersorten/alkoholfrei",
            "https://www.bierlinie-shop.de/biersorten/alt-biere",
            "https://www.bierlinie-shop.de/biersorten/american-ale",
            "https://www.bierlinie-shop.de/biersorten/american-lager",
            "https://www.bierlinie-shop.de/biersorten/barley-wine",
            "https://www.bierlinie-shop.de/biersorten/barrel-aged",
            "https://www.bierlinie-shop.de/biersorten/bayrisch-dunkel",
            "https://www.bierlinie-shop.de/biersorten/belgisches-ale",
            "https://www.bierlinie-shop.de/biersorten/belgisches-starkbier",
            "https://www.bierlinie-shop.de/biersorten/berliner-weisse",
            "https://www.bierlinie-shop.de/biersorten/biere-brut",
            "https://www.bierlinie-shop.de/biersorten/biere-de-garde",
            "https://www.bierlinie-shop.de/biersorten/biere-mit-kaffee-aromen",
            "https://www.bierlinie-shop.de/biersorten/biere-mit-rauch-aromen",
            "https://www.bierlinie-shop.de/biersorten/bitter",
            "https://www.bierlinie-shop.de/biersorten/bio-biere",
            "https://www.bierlinie-shop.de/biersorten/blond",
            "https://www.bierlinie-shop.de/biersorten/bock-doppelbock",
            "https://www.bierlinie-shop.de/biersorten/brown-ale",
            "https://www.bierlinie-shop.de/biersorten/bruin-brune",
            "https://www.bierlinie-shop.de/biersorten/cider",
            "https://www.bierlinie-shop.de/biersorten/craft-beer",
            "https://www.bierlinie-shop.de/biersorten/dubbel-double",
            "https://www.bierlinie-shop.de/biersorten/double-ipa",
            "https://www.bierlinie-shop.de/biersorten/dunkel",
            "https://www.bierlinie-shop.de/biersorten/eisbock",
            "https://www.bierlinie-shop.de/biersorten/exotische-biere",
            "https://www.bierlinie-shop.de/biersorten/export",
            "https://www.bierlinie-shop.de/biersorten/extra-special-bitter-esb",
            "https://www.bierlinie-shop.de/biersorten/faro",
            "https://www.bierlinie-shop.de/biersorten/flavoured-beer",
            "https://www.bierlinie-shop.de/biersorten/flaemisch-rotbraun",
            "https://www.bierlinie-shop.de/biersorten/frucht-ipa",
            "https://www.bierlinie-shop.de/biersorten/fruchtbier",
            "https://www.bierlinie-shop.de/biersorten/fruchtlambic",
            "https://www.bierlinie-shop.de/biersorten/fruehlingsbiere",
            "https://www.bierlinie-shop.de/biersorten/glutenfreie-biere",
            "https://www.bierlinie-shop.de/biersorten/grand-crus",
            "https://www.bierlinie-shop.de/biersorten/gueuze",
            "https://www.bierlinie-shop.de/biersorten/hefeweizen",
            "https://www.bierlinie-shop.de/biersorten/helles",
            "https://www.bierlinie-shop.de/biersorten/herbstbiere",
        ]

        # Add '?items=100' to retrieve 100 products per page and click between pages less
        urls = [f"{url}?items=100" for url in urls]

        for url in urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True},
            )

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        # inspect_response(response, self)

        products = response.xpath("//article[contains(@class, 'cmp-product-thumb')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                style = (
                    response.url.split("/")[-1]
                    .replace("?items=100", "")
                    .replace("-", " ")
                    .title()
                )

                product_url = product.xpath(".//div[@class='thumb-image']//a/@href").get()
                product_url = f"{self.main_url}{product_url}"

                availability = product.xpath(
                    ".//div[@class='thumb-content']//button[contains(@class, 'button-basket')]"
                ).get()
                available = bool(availability)

                volume_info = product.xpath(
                    ".//div[@class='category-unit-price']//span/text()"
                ).getall()
                volume = volume_info[0] + volume_info[1]
                price_per_liter = volume_info[2]

                loader.add_value("vendor", self.name)
                loader.add_value("style", style)

                loader.add_xpath("name", ".//div[@class='thumb-image']//img/@title")
                loader.add_value("available", available)

                loader.add_value("product_url", product_url)
                loader.add_xpath("image_url", ".//div[@class='thumb-image']//img/@src")
                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath(
                    "price_eur", ".//div[@class='price']//span[@class='price-value']/text()"
                )
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value("on_sale", False)
                loader.add_value("original_price", None)
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
