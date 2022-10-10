import json

from loguru import logger
from playwright.sync_api import sync_playwright
from datetime import datetime
from scrapy import Selector

from beerspider.items import ProductItemLoader, volume_str_to_float
from beerspider.utils import get_project_dir


class FlaschenpostManualSpider:
    name = "flaschenpost"
    main_url = "https://www.flaschenpost.de/"
    scrape_headless = True
    success_counter = 0

    urls = (
        "https://www.flaschenpost.de/bier/pils",
        "https://www.flaschenpost.de/bier/helles",
        "https://www.flaschenpost.de/bier/alkoholfrei",
        "https://www.flaschenpost.de/bier/radler-biermix",
        "https://www.flaschenpost.de/bier/weizenbier",
        "https://www.flaschenpost.de/bier/koelsch",
        "https://www.flaschenpost.de/bier/land-kellerbier",
        "https://www.flaschenpost.de/bier/malzbier",
        "https://www.flaschenpost.de/bier/internationale-biere",
        "https://www.flaschenpost.de/bier/spezialitaeten"
    )

    scraped_products: list[dict] = []

    def __init__(self, scrape_headless: bool = True):
        self.scrape_headless = scrape_headless

    def parse_urls(self):
        for url in self.urls:
            for plz in (10115, ):  # 20251, 48151, 60313, 80337):
                with sync_playwright() as playwrighter:
                    browser = playwrighter.chromium.launch(
                        headless=self.scrape_headless, slow_mo=500
                    )
                    page = browser.new_page()
                    page.goto(url)

                    logger.info(page.title())
                    page.locator("//div[@class='zipcode_input_component']//input").fill(str(plz))
                    page.wait_for_selector(
                        "//button[@class='fp_button fp_button_primary fp_button_large']"
                    )
                    page.click("//button[@class='fp_button fp_button_primary fp_button_large']")
                    page.wait_for_selector("//div[@class='fp_product']")
                    page.wait_for_timeout(5000)

                    page_content = page.content()
                    selector = Selector(text=page_content)

                    products = selector.xpath("//div[@class='fp_product']")
                    products_on_sale = selector.xpath("//div[@class='fp_product isOffer']")
                    num_products = len(products + products_on_sale)
                    logger.info(
                        f"Found {num_products} products on page {url}, starting to crawl..."
                    )
                    self.success_counter = 0

                    for product in products:
                        self.parse_product(product=product, url=url)

                    for product in products_on_sale:
                        self.parse_product(product=product, url=url, on_sale=True)

                    logger.info(
                        f"Finished crawling {url}. Successfully crawled {self.success_counter} "
                        f"out of {num_products} products!"
                    )

    def parse_product(self, product: Selector, url: str, on_sale: bool = False):
        """

        :param product:
        :param url:
        :param on_sale:
        """
        try:
            logger.info("parsing...")
            style = url.split("/")[-1].replace("-", " ").title()

            image_url = product.css("a.fp_product_image").attrib.get("href")
            image_url = f"{self.main_url[:-1]}{image_url}"

            original_price = None

            varieties = product.xpath(
                ".//div[contains(@class, 'fp_article bottleTypeExists')]"
            )

            for variety in varieties:
                loader = ProductItemLoader(selector=product)

                loader.add_value("vendor", self.name)
                loader.add_value("style", style)

                loader.add_value("image_url", image_url)
                loader.add_css("product_url", "a.fp_product_image > img::attr(src)")

                loader.add_value("scraped_from_url", url)

                loader.add_css("name", "h5.fp_product_name::text")
                loader.add_value("available", True)

                # TODO: price is currently problematic as it differs per provided PLZ
                price_eur = variety.css("div.fp_article_price::text").get()

                total_volume = (
                    variety.css("div.fp_article_bottleInfo::text").get().split("x")
                )
                amount = int(total_volume[0].strip())
                bottle_volume = volume_str_to_float(
                    total_volume[1].strip().replace("(Glas)", "")
                )
                volume = amount * bottle_volume

                price_per_liter = variety.css(
                    "div.fp_article_pricePerUnit_deposit::text"
                ).get()
                price_per_liter = price_per_liter.split(")")[0].replace("(", "")
                logger.info(f"Price in EUR and per liter: {price_eur}, {price_per_liter}")

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", str(volume))
                loader.add_value("price_eur_per_liter", price_per_liter)

                if on_sale:
                    original_price = variety.css(
                        "div.fp_article_price_stroked::text"
                    ).get()

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)

                loader.load_item()
                logger.info(loader.item.__dict__)
                self.scraped_products.append(loader.item.__dict__.get("_values"))
                self.success_counter += 1

        except Exception as e:
            logger.error(f"Error {e} occurred...")

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
    flaschenpost_spider = FlaschenpostManualSpider()
    flaschenpost_spider.parse_urls()
    flaschenpost_spider.export_results()
