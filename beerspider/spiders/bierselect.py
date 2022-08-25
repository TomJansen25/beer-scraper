import scrapy
from loguru import logger

from beerspider.items import ProductItemLoader


class BierSelectSpider(scrapy.Spider):
    """
    The BierSelect Spider used to crawl Breweries and Beers from bierselect.de
    """

    name = "BierSelect"
    main_url = "https://bierselect.de/"

    def start_requests(self):
        urls = [
            "https://bierselect.de/Bock-und-Doppelbock_1",
            "https://bierselect.de/Alkoholfrei_1",
            "https://bierselect.de/Export_1",
            "https://bierselect.de/Maerzen_1",
            "https://bierselect.de/Rauchbier_1",
            "https://bierselect.de/Gourmetflaschen",
            "https://bierselect.de/Hell-und-Lager_1",
            "https://bierselect.de/Pils_1",
            "https://bierselect.de/Spezialbier_1",
            "https://bierselect.de/Neuheiten_1",
            "https://bierselect.de/Craft-Beer_1",
            "https://bierselect.de/India-Pale-Ale_1",
            "https://bierselect.de/Porter-und-Stout_1",
            "https://bierselect.de/Winterbiere",
            "https://bierselect.de/Ale-und-Pale-Ale_1",
            "https://bierselect.de/Dunkel_1",
            "https://bierselect.de/Kellerbier_1",
            "https://bierselect.de/Radler_1",
            "https://bierselect.de/Weizen_1"
            # 'https://bierselect.de/Sale-'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.product-wrapper")
        logger.info(f"Found {len(products)} products on page {response.url}, starting to crawl...")
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                name = product.xpath('.//div[@class="caption"]//h4//a/text()').get()
                # Skip this beer if it is a package
                if "paket" in name.lower():
                    continue

                availability = product.xpath(
                    './/div[@class="delivery-status"]//div//small/text()'
                ).get()
                available = True
                if availability == "momentan nicht verfügbar":
                    available = False

                prices = product.xpath(
                    './/strong[@class="price text-nowrap"]//span/text()'
                ).getall()

                if len(prices) == 2:
                    on_sale, original_price = False, None
                elif len(prices) > 2 and prices[1] == "%":
                    on_sale, original_price = True, prices[3]
                else:
                    self.logger.warning(
                        "Could not figure out whether product on sale or not. Product will be ignored."
                    )
                    continue

                volume = product.xpath(
                    './/div[@class="base_price text-nowrap"]/text()'
                ).getall()[2]

                loader.add_value("vendor", self.name)
                loader.add_value(
                    "style",
                    response.url.split("/")[-1]
                    .replace("_1", "")
                    .replace("_s2", "")
                    .replace("_s3", ""),
                )

                loader.add_xpath("product_url", './/div[@class="caption"]//meta/@content')
                loader.add_xpath(
                    "image_url", './/div[@class="image-content"]//meta/@content'
                )

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_xpath(
                    "price_eur", './/strong[@class="price text-nowrap"]//span[1]/text()'
                )
                loader.add_value("volume_liter", volume)
                loader.add_xpath(
                    "price_eur_per_liter", './/span[@class="value hidden-xs"]/text()'
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)

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
            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
