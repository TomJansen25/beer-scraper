from loguru import logger
from scrapy import Request, Spider
from scrapy.shell import inspect_response
from scrapy.utils.reactor import install_reactor, verify_installed_reactor

from beerspider.items import (
    ProductItemLoader,
    price_str_to_float,
    price_volume_str_to_float,
)

if not verify_installed_reactor(
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
):
    logger.info("AsyncioSelectorReactor not installed yet and will be installed...")
    install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")


class MeibierSpider(Spider):
    name = "Meibier"
    allowed_domains = ["meibier.de"]
    main_url = "https://www.meibier.de/"

    def start_requests(self):
        urls = ["https://www.meibier.de/c/biersorten/weizenbier"]
        urls = [f"{url}?page=20" for url in urls]

        for url in urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta=dict(
                    playwright=True,
                ),
            )

    @logger.catch
    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("div.product-item")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        # inspect_response(response, self)

        for product in products:

            try:

                loader = ProductItemLoader(selector=product)

                out_of_stock = product.xpath(
                    ".//span[contains(@class, 'out-stock-icon')]"
                ).get()
                available = not bool(out_of_stock)

                image_srcset = product.xpath(
                    ".//img[contains(@class, 'product-item-image')]/@srcset"
                ).get()
                image_url = None
                if image_srcset:
                    image_url = image_srcset.split(" ")[0]

                loader.add_value("vendor", self.name)
                loader.add_value(
                    "style", response.url.split("/")[-1].replace("?page=20", "").title()
                )

                product_url = product.css("a.product-item-link::attr(href)").get()
                loader.add_value("product_url", f"{self.main_url[:-1]}{product_url}")
                loader.add_value("image_url", f"{self.main_url[:-1]}{image_url}")

                loader.add_value("scraped_from_url", response.url)

                loader.add_css("name", "h2.product-item-title::text")
                loader.add_value("available", available)

                price_eur = product.xpath(
                    ".//div[@class='product-item-price']//div//meta[@itemprop='price']/@content"
                ).get()

                price_per_liter = product.css(
                    "span.product-item-price-reference::text"
                ).getall()
                if price_per_liter and len(price_per_liter) > 2:
                    price_eur_per_liter = price_volume_str_to_float(
                        price_per_liter[1].replace("1 l =", "")
                    )
                    volume_liter = float(price_eur) / price_eur_per_liter
                else:
                    price_eur_per_liter, volume_liter = None, None

                loader.add_value("price_eur", str(price_eur))
                loader.add_value("volume_liter", str(volume_liter))
                loader.add_value("price_eur_per_liter", str(price_eur_per_liter))

                old_price = product.css("h3.product-item-price-old").get()
                on_sale = bool(old_price)

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", old_price)

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
