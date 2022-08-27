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

        # Add 'af=50' to retrieve 50 products per page since next page link is missing...
        urls = [f"{url}?af=50" for url in urls]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div#product-list > div.product-wrapper")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                name = product.xpath(".//h4[@class='productbox-title']//a/text()").get()
                # Skip this beer if it is a package
                if not name or "paket" in name.lower():
                    continue

                availability = product.xpath(
                    './/div[@class="delivery-status"]//div//small/text()'
                ).get()
                available = True
                if availability == "momentan nicht verfügbar":
                    available = False

                price_eur = product.xpath(
                    ".//div[@class='price_wrapper']//meta[@itemprop='price']/@content"
                ).get()

                prices = product.xpath(
                    './/strong[@class="price text-nowrap"]//span/text()'
                ).getall()
                if len(prices) > 1:
                    on_sale, original_price = True, prices[3]
                else:
                    on_sale, original_price = False, None

                volumes = product.xpath(".//div[@class='base_price']/text()").getall()
                volume = next(v for v in volumes if "Liter" in v)

                loader.add_value("vendor", self.name)
                loader.add_value(
                    "style",
                    response.url.split("/")[-1]
                    .replace("?af=50", "")
                    .replace("_1", "")
                    .replace("_s2", "")
                    .replace("_s3", ""),
                )

                loader.add_xpath(
                    "product_url", ".//h4[@class='productbox-title']//a/@href"
                )
                loader.add_xpath(
                    "image_url",
                    ".//div[contains(@class, 'productbox-image')]//img/@src",
                )

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", volume)
                loader.add_xpath(
                    "price_eur_per_liter",
                    './/div[@class="base_price"]//meta[@itemprop="price"]/@content',
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)

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
        next_page = response.css("li.next > a").attrib.get("href")
        if next_page is not None:
            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
