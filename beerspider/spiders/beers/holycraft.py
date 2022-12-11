from datetime import datetime

from loguru import logger
from scrapy import Request, Spider

from beerspider.items import ProductItemLoader
from beerspider.settings import NAME_CONTAINS_EXCLUDE


class HolyCraftSpider(Spider):
    """
    The Holy Craft Spider used to crawl Beers from holycraft.de
    """

    name = "holycraft"
    allowed_domains = ["holycraft.de"]
    main_url = "https://holycraft.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def start_requests(self):
        urls = [
            "https://holycraft.de/Alkoholfreies-Bier",
            "https://holycraft.de/Altbier",
            "https://holycraft.de/Barley-Wine",
            "https://holycraft.de/Belgische-Stile",
            "https://holycraft.de/Bockbier",
            "https://holycraft.de/Cider"
            "https://holycraft.de/Fassgereift",
            "https://holycraft.de/Fruited",
            "https://holycraft.de/Glutenfreies-Bier",
            "https://holycraft.de/Gose",
            "https://holycraft.de/India-Pale-Ale",
            "https://holycraft.de/Koelsch-Wiess",
            "https://holycraft.de/Lager-Pilsner-Helles",
            "https://holycraft.de/Pale-Ale-Golden-Ale",
            "https://holycraft.de/Porter-Stout",
            "https://holycraft.de/Red-Brown-Amber-Ale",
            "https://holycraft.de/Sommer-Biere",
            "https://holycraft.de/Sour-Wild",
            "https://holycraft.de/Spiced-Herbed",
            "https://holycraft.de/Strong-Old-Scotch-Ale",
            "https://holycraft.de/Weizen",
        ]

        # Add 'af=50' to retrieve 50 products per page to reduce moving between pages
        urls = [f"{url}?af=50" for url in urls]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.xpath("//div[contains(@class, 'product-wrapper')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                full_name = product.xpath(".//h4[@class='product-cell__title title']/a/text()").get()
                if any(n in full_name.lower() for n in NAME_CONTAINS_EXCLUDE):
                    continue
                else:
                    full_name = full_name.rpartition(" ")
                    name, _, volume = full_name

                in_cart = product.xpath(".//button[@name='inWarenkorb']")
                available = bool(in_cart)

                loader.add_value("vendor", self.name)
                loader.add_value("style", response.url.split("/")[-1].replace("?af=50", ""))

                loader.add_xpath("product_url", ".//a[@class='image-wrapper ']/@href")
                loader.add_xpath(
                    "image_url", 
                    ".//div[contains(@class, 'mediabox-img-wrapper')]/picture/source/img/@data-lowsrc"
                )

                loader.add_value("scraped_from_url", response.url)

                loader.add_value("name", name)
                loader.add_value("available", available)

                loader.add_xpath(
                    "price_eur", ".//strong[@class='price ']/meta[@itemprop='price']/@content"
                )
                loader.add_value("volume_liter", volume)

                price_per_100_ml = product.xpath(
                    ".//div[@class='base-price']/meta[@itemprop='price']/@content"
                ).get()
                loader.add_value("price_eur_per_liter", str(float(price_per_100_ml) * 10))

                # loader.add_value("on_sale",)
                # loader.add_xpath("original_price",)

                yield loader.load_item()
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
        next_page = response.css("li.next > a").attrib.get("href")
        if next_page is not None:
            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
