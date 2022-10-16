from scrapy import Selector
from playwright.sync_api import sync_playwright
from datetime import datetime
from loguru import logger

from beerspider.items import ProductItemLoader


class ReweShopSpider:
    """
    REWE Online Shop Spider Class
    """

    name = "REWE Shop"
    allowed_domains = ["shop.rewe.de"]
    main_url = "https://www.craftbeer-shop.com/"
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

    def parse_urls(self):
        urls = [f"{url}?objectsPerPage=80" for url in self.urls]
        for url in urls[:3]:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=self.scrape_headless, slow_mo=500
                    )
                    page = browser.new_page()
                    page.goto(url)
                    page.wait_for_timeout(timeout=5000)
                    page.click("//button[@id='uc-btn-accept-banner']")
                    page.click(
                        "//button[contains(@class, 'gbmc-qa-delivery-intention')]"
                    )
                    page.locator(
                        "//input[contains(@class, 'gbmc-zipcode-input')]"
                    ).fill(str(10115))
                    logger.info(page.title())

            except Exception as e:
                logger.error(f"ERROR: {e}")
