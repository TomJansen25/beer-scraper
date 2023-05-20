import re
from datetime import datetime
from math import prod

from loguru import logger
from playwright.sync_api import sync_playwright
from scrapy import Selector

from beerspider.items import NUMBER_PATTERN, ProductItemLoader


class ReweShopSpider:
    """
    REWE Online Shop Spider Class
    """

    name = "REWE Shop"
    allowed_domains = ["shop.rewe.de"]
    main_url = "https://shop.rewe.de/"
    datestamp = datetime.now().strftime("%Y_%m_%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    urls = [
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-alkoholfreies-bier/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-besondere-biere/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-bock-starkbier/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-export/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-helles-bier/"
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-kellerbier/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-koelsch/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-lagerbier/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-pils/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-schwarzbier/",
        "https://shop.rewe.de/c/getraenke-bier-mischgetraenke-bier-weissbier/",
    ]

    scraped_products: list[dict] = []

    def __init__(self, scrape_headless: bool = True):
        self.scrape_headless = scrape_headless

    def parse_page_content(self, page_content: str, url: str):
        selector = Selector(text=page_content)
        products = selector.xpath(
            "//div[contains(@class, 'search-service-productDetailsWrapper')]"
        )

        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            # try:
            print("scraping....")
            loader = ProductItemLoader(selector=product)

            loader.add_value("vendor", self.name)
            loader.add_value(
                "style",
                url.split("/")[-2]
                .replace("getraenke-bier-mischgetraenke-bier-", "")
                .replace("-", " "),
            )

            product_url = product.xpath(
                "a[contains(@class, 'search-service-productDetailsLink')]/@href"
            ).get()

            loader.add_value("product_url", f"{self.main_url}{product_url[1:]}")
            loader.add_xpath(
                "image_url",
                "//div[contains(@class, 'search-service-rsProductsMedia')]/picture//img/@src",
            )

            loader.add_xpath(
                "name",
                "//h4[contains(@class, 'search-service-productTitle')]//div/text()",
            )
            loader.add_value("available", True)

            price_specs = product.xpath(
                "//div[contains(@class, 'search-service-productGrammage')]//div/text()"
            ).get()
            price_eur = product.xpath(
                "//div[contains(@class, 'search-service-productPrice')]/text()"
            ).get()

            loader.add_value("price_eur", price_eur)
            """
            print(price_specs)

            if "(1 l =" in price_specs:
                volume, price_eur_per_liter = price_specs.split("(")
                price_eur_per_liter = price_eur_per_liter.replace("1 l =", "").replace(
                    ")", ""
                )

                if "x" in volume:
                    pieces, individual_volume = volume.split("x")
                else:
                    pieces, individual_volume = 1, volume

                individual_volume = individual_volume.replace(",", ".")
                print(individual_volume)
                individual_volume = float(
                    re.search(NUMBER_PATTERN, individual_volume)[0]
                )
            else:
                price_eur_per_liter = price_eur
                pieces, volume, individual_volume = 1, 1, 1

            total_volume = float(pieces) * individual_volume

            loader.add_value("volume_liter", total_volume)
            loader.add_value("price_eur_per_liter", price_eur_per_liter)
            loader.add_value("on_sale", False)
            """
            loader.load_item()
            logger.info(loader.item.__dict__)
            self.scraped_products.append(loader.item.__dict__.get("_values"))
            success_counter += 1

        # except Exception as e:
        #   logger.error(f"ERROR: {e}")

    def parse_urls(self):
        urls = [f"{url}?objectsPerPage=80" for url in self.urls]
        for url in urls[:2]:
            # try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.scrape_headless, slow_mo=500)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_timeout(timeout=5000)
                page.click("//button[@id='uc-btn-accept-banner']")
                page.click("//button[contains(@class, 'gbmc-qa-delivery-intention')]")
                page.locator("//input[contains(@class, 'gbmc-zipcode-input')]").fill(
                    str(10115)
                )
                logger.info(page.title())

                page_content = page.content()
                self.parse_page_content(page_content, url)

        # except Exception as e:
        #   logger.error(f"ERROR: {e}")
