import json
from datetime import datetime

from loguru import logger
from playwright.sync_api import sync_playwright
from scrapy import Selector

from beerspider.items import ProductItemLoader, volume_str_to_float
from beerspider.utils import get_project_dir


class BierlinieManualSpider:
    name = "bierlinie"
    main_url = "https://www.bierlinie-shop.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    scrape_headless = True
    scrape_from_germany = True

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
        "https://www.bierlinie-shop.de/biersorten/holzgereifte-biere",
        "https://www.bierlinie-shop.de/biersorten/honig-bier",
        "https://www.bierlinie-shop.de/biersorten/imperial-ipa",
        "https://www.bierlinie-shop.de/biersorten/imperial-stout",
        "https://www.bierlinie-shop.de/biersorten/india-pale-ale",
        "https://www.bierlinie-shop.de/biersorten/kirschbier",
        "https://www.bierlinie-shop.de/biersorten/koelsch",
        "https://www.bierlinie-shop.de/biersorten/kraeusen-kellerbier-zwickel",
        "https://www.bierlinie-shop.de/biersorten/kraeuter-und-gewuerzbiere",
        "https://www.bierlinie-shop.de/biersorten/kristall",
        "https://www.bierlinie-shop.de/biersorten/lager",
        "https://www.bierlinie-shop.de/biersorten/lambic",
        "https://www.bierlinie-shop.de/biersorten/leichtbier",
        "https://www.bierlinie-shop.de/biersorten/limited-edition",
        "https://www.bierlinie-shop.de/biersorten/maerzen",
        "https://www.bierlinie-shop.de/biersorten/new-england-ipa",
        "https://www.bierlinie-shop.de/biersorten/oktoberfestbier",
        "https://www.bierlinie-shop.de/biersorten/oud-bruin",
        "https://www.bierlinie-shop.de/biersorten/pale-ale",
        "https://www.bierlinie-shop.de/biersorten/pils",
        "https://www.bierlinie-shop.de/biersorten/porter",
        "https://www.bierlinie-shop.de/biersorten/radler",
        "https://www.bierlinie-shop.de/biersorten/regionale-spezialitaeten",
        "https://www.bierlinie-shop.de/biersorten/quadrupel",
        "https://www.bierlinie-shop.de/biersorten/reisbier",
        "https://www.bierlinie-shop.de/biersorten/saison",
        "https://www.bierlinie-shop.de/biersorten/sauerbier",
        "https://www.bierlinie-shop.de/biersorten/session-ipa",
        "https://www.bierlinie-shop.de/biersorten/schwarzbier",
        "https://www.bierlinie-shop.de/biersorten/single-enkel",
        "https://www.bierlinie-shop.de/biersorten/sommerbiere",
        "https://www.bierlinie-shop.de/biersorten/speciale-belge",
        "https://www.bierlinie-shop.de/biersorten/spezial",
        "https://www.bierlinie-shop.de/biersorten/starkbier",
        "https://www.bierlinie-shop.de/biersorten/stout",
        "https://www.bierlinie-shop.de/biersorten/strong-golden-ale",
        "https://www.bierlinie-shop.de/biersorten/teufelsbiere",
        "https://www.bierlinie-shop.de/biersorten/trappistenbier",
        "https://www.bierlinie-shop.de/biersorten/tripel",
        "https://www.bierlinie-shop.de/biersorten/veganes-bier",
        "https://www.bierlinie-shop.de/biersorten/weihnachtsbier",
        "https://www.bierlinie-shop.de/biersorten/weissbier",
        "https://www.bierlinie-shop.de/biersorten/weizenbier",
        "https://www.bierlinie-shop.de/biersorten/winterbiere",
        "https://www.bierlinie-shop.de/biersorten/witbier",
    ]

    scraped_products: list[dict] = []

    def __init__(self, scrape_headless: bool = True, scrape_from_germany: bool = True):
        self.scrape_headless = scrape_headless
        self.scrape_from_germany = scrape_from_germany

    def parse_page_content(self, page_content: str, url: str):
        selector = Selector(text=page_content)
        products = selector.xpath("//article[contains(@class, 'cmp-product-thumb')]")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                # logger.info(product.get())
                logger.info(
                    product.xpath(
                        ".//div[@class='category-unit-price']//span/text()"
                    ).get()
                )

                product_name = product.xpath(
                    ".//div[@class='thumb-content']//a/text()"
                ).get()
                # Check for names of products to exclude from scraping
                if any(
                    n in product_name.lower()
                    for n in [
                        "paket",
                        "package",
                        "box",
                        "überraschungsbier",
                        "geschenk set",
                    ]
                ):
                    continue

                style = (
                    url.split("/")[-1]
                    .replace("?items=100", "")
                    .replace("-", " ")
                    .title()
                )

                product_url = product.xpath(
                    ".//div[@class='thumb-image']//a/@href"
                ).get()
                product_url = f"{self.main_url[:-1]}{product_url}"

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

                loader.add_value("name", product_name)
                loader.add_xpath(
                    "description", ".//div[@class='thumb-image']//img/@alt"
                )
                loader.add_value("available", available)

                loader.add_value("product_url", product_url)
                loader.add_xpath(
                    "image_url", ".//div[@class='thumb-image']//source/@srcset"
                )
                loader.add_value("scraped_from_url", url)

                loader.add_xpath(
                    "price_eur",
                    ".//div[@class='price']//span[@class='price-value']/text()",
                )
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value("on_sale", False)
                loader.add_value("original_price", None)
                loader.add_value("discount", None)

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
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=self.scrape_headless, slow_mo=500
                    )
                    page = browser.new_page()
                    page.goto(url)

                    logger.info(page.title())
                    page.wait_for_timeout(100)

                    page.click("//button[@data-testing='cookie-bar-deny-all']")

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
            save_dir.joinpath(f"bierlinie_{timestamp}.json"), "w", encoding="utf-8"
        ) as save_file:
            json.dump(self.scraped_products, save_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    bierlinie_spider = BierlinieManualSpider(scrape_headless=False)
    bierlinie_spider.parse_urls()
    bierlinie_spider.export_results()
