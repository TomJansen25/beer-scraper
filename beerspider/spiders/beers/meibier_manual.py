import json
from datetime import datetime

from loguru import logger
from scrapy import Selector

from playwright.sync_api import sync_playwright

# from scrapy.shell import inspect_response
# from scrapy.utils.reactor import install_reactor, verify_installed_reactor

from beerspider.items import ProductItemLoader, price_volume_str_to_float
from beerspider.settings import NAME_CONTAINS_EXCLUDE
from beerspider.utils import get_project_dir


class MeibierManuelSpider:
    name = "meibier"
    main_url = "https://www.meibier.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    scrape_headless = True

    urls = [
        "https://www.meibier.de/c/biersorten/alkoholfreies-bier",
        "https://www.meibier.de/c/biersorten/bio-oder-glutenfreies-bier",
        "https://www.meibier.de/c/biersorten/bockbier-oder-festbier",
        "https://www.meibier.de/c/biersorten/craftbier-oder-spezialitaeten",
        "https://www.meibier.de/c/biersorten/dunkle-biere",
        "https://www.meibier.de/c/biersorten/hell-oder-lager-oder-landbier",
        "https://www.meibier.de/c/biersorten/kellerbier-oder-zwickelbier",
        "https://www.meibier.de/c/biersorten/maerzen",
        "https://www.meibier.de/c/biersorten/pils",
        "https://www.meibier.de/c/biersorten/radler-oder-biermix-oder-leichtes-bier",
        "https://www.meibier.de/c/biersorten/rauchbier",
        "https://www.meibier.de/c/biersorten/schwarzbier",
        "https://www.meibier.de/c/biersorten/weizenbier",
    ]

    scraped_products: list[dict] = []

    def __init__(self, scrape_headless: bool = True):
        self.scrape_headless = scrape_headless

    def parse_page_content(self, page_content: str, url: str):
        selector = Selector(text=page_content)
        products = selector.css("div.product-item")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                product_name = product.css("h2.product-item-title::text").get()
                if any(n in product_name.lower() for n in NAME_CONTAINS_EXCLUDE):
                    continue

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
                    image_url = f"{self.main_url[:-1]}{image_url}"

                loader.add_value("vendor", self.name)
                loader.add_value(
                    "style",
                    url.split("/")[-1]
                    .replace("?page=20", "")
                    .replace("-oder-", " | ")
                    .replace("-", " ")
                    .title(),
                )

                product_url = product.css("a.product-item-link::attr(href)").get()
                loader.add_value("product_url", f"{self.main_url[:-1]}{product_url}")
                loader.add_value("image_url", image_url)

                loader.add_value("scraped_from_url", url)

                loader.add_value("name", product_name)
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

                loader.load_item()
                logger.info(loader.item.__dict__)
                self.scraped_products.append(loader.item.__dict__.get("_values"))
                success_counter += 1

            except Exception as e:
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling page {url}! "
            f"Successfully crawled {success_counter} out of {num_products} products!"
        )

    def parse_urls(self):
        for url in self.urls:
            url = f"{url}?page=20"
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=self.scrape_headless, slow_mo=500
                    )
                    page = browser.new_page()
                    page.goto(url)

                    logger.info(page.title())
                    page.wait_for_timeout(100)

                    page.click("//button[@aria-label='Nein, anpassen']")

                    page.wait_for_timeout(100)

                    page_content = page.content()
                    self.parse_page_content(page_content, url)

                    browser.close()

            except Exception as e:
                logger.error(f"ERROR: {e}")

    def export_results(self):
        datestamp = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        save_dir = get_project_dir().joinpath("data", datestamp)
        save_dir.mkdir(exist_ok=True)
        with open(
            save_dir.joinpath(f"{self.name}_{timestamp}.json"), "w", encoding="utf-8"
        ) as save_file:
            json.dump(self.scraped_products, save_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    meibier_spider = MeibierManuelSpider(scrape_headless=False)
    meibier_spider.parse_urls()
    meibier_spider.export_results()
