import json

from loguru import logger
from playwright.sync_api import sync_playwright
from datetime import datetime
from scrapy import Selector

from beerspider.items import ProductItemLoader, volume_str_to_float
from beerspider.utils import get_project_dir


class BeertastingManualSpider:
    name = "beertasting"
    main_url = "https://www.beertasting.com/"
    scrape_headless = True

    urls = [
        "https://www.beertasting.com/de-de/biere/ale-angloamerikanisch",
        "https://www.beertasting.com/de-de/biere/ale-belgisch",
        "https://www.beertasting.com/de-de/biere/alkoholfrei",
        "https://www.beertasting.com/de-de/biere/biermischgetranke~c1788390",
        "https://www.beertasting.com/de-de/biere/bock",
        "https://www.beertasting.com/de-de/biere/cider",
        "https://www.beertasting.com/de-de/biere/dunkles-lager",
        "https://www.beertasting.com/de-de/biere/helles-lager",
        "https://www.beertasting.com/de-de/biere/india-pale-ale",
        "https://www.beertasting.com/de-de/biere/kreativbier",
        "https://www.beertasting.com/de-de/biere/nachreifung",
        "https://www.beertasting.com/de-de/biere/obergarige-leichtbiere~c1788399",
        "https://www.beertasting.com/de-de/biere/porter-stout",
        "https://www.beertasting.com/de-de/biere/sauergarung~c1788401",
        "https://www.beertasting.com/de-de/biere/weissbier",
        "https://www.beertasting.com/de-de/glutenfrei~c2229548",
    ]

    scraped_products: list[dict] = []

    def __init__(self, scrape_headless: bool = True):
        self.scrape_headless = scrape_headless

    def parse_page_content(self, page_content: str, url: str):
        # page_html = html.fromstring(page_content)
        selector = Selector(text=page_content)
        products = selector.xpath("//div[contains(@class, 'bts-product-item--beer')]")

        num_products = len(products)
        logger.info(f"Found {num_products} products on page {url}, starting to crawl...")
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                product_link = product.xpath(
                    ".//div[@class='card-body d-flex flex-column']//a/@href"
                ).get()
                product_url = f"{self.main_url}{product_link[1:]}"

                discount_badge = product.xpath(
                    ".//div[@class='bts-product-badges__item is--discounted']"
                )
                on_sale = bool(discount_badge.get())

                if on_sale:
                    original_price = product.xpath(
                        ".//p[@class='js-discount-price product-price__original']/text()"
                    ).get()
                    discount = discount_badge.css("span.item-label::text").get()
                else:
                    original_price, discount = None, None

                availability = product.xpath(
                    ".//div[@class='bts-product-item__availability']/text()"
                ).get()
                available = False
                if availability.strip() == "Auf Lager":
                    available = True

                content = product.xpath(
                    ".//div[contains(@class, 'bts-product-item__content-wrapper')]"
                )
                meta_information = content.css(
                    "div.content-wrapper__top > div.bts-product-item__meta-information"
                )

                first_line_meta = meta_information.xpath(
                    "./div[@class='first-line']/text()"
                ).getall()
                style = first_line_meta[0]
                volume = first_line_meta[1]

                unit = product.xpath(
                    ".//span[@class='js-unit-definition-name']/text()"
                ).get()

                if "er Box" in unit:
                    amount = int(unit.replace("er Box", ""))
                    volume = volume_str_to_float(volume) * amount

                loader.add_value("vendor", self.name)
                loader.add_value("style", style)

                loader.add_value("product_url", product_url)
                loader.add_xpath(
                    "image_url", ".//img[@class='bts-product-item__image']/@src"
                )

                loader.add_value("scraped_from_url", url)

                loader.add_xpath("name", ".//p[@class='bts-product-item__name']/text()")
                loader.add_xpath(
                    "description",
                    ".//div[@class='bts-product-item__description']//p/text()",
                )
                loader.add_value("available", available)

                loader.add_xpath(
                    "price_eur",
                    ".//p[@class='js-retail-price product-price__default']/text()",
                )
                loader.add_value("volume_liter", str(volume))
                loader.add_xpath(
                    "price_eur_per_liter",
                    ".//p[@class='bts-product-item__price-information']//"
                    "span[@class='js-base-price']/text()",
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)
                loader.add_value("discount", discount)

                loader.load_item()
                # logger.info(loader.item.__dict__)
                self.scraped_products.append(loader.item.__dict__.get("_values"))
                success_counter += 1

            except Exception as e:
                logger.error(f"ERROR: {e}")

        curr_page = int(
            selector.xpath(
                ".//ul[@class='pagination b-pagination']//li[@class='page-item active']//a/text()"
            ).get()
        )
        logger.info(
            f"Finished crawling page {curr_page} of {url}! "
            f"Successfully crawled {success_counter} out of {num_products} products!"
        )

    def parse_urls(self):
        for url in self.urls:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.scrape_headless, slow_mo=500)
                    page = browser.new_page()
                    page.goto(url)

                    logger.info(page.title())

                    # page.click("//a[contains(@class, 'cmpboxbtnno')]")
                    # page.click("//div[@id='country-modal___BV_modal_body_']//button[@class='btn btn-outline-dark']")
                    page.click("//div[contains(@class, 'bts-per-page-select')]//button")
                    page.click("//a[@id='bs-select-1-2']")

                    page_content = page.content()
                    self.parse_page_content(page_content, url)

                    next_page_available = True
                    while next_page_available:
                        # page_html = html.fromstring(page_content)
                        selector = Selector(text=page_content)
                        current_page = int(
                            selector.xpath(
                                ".//ul[@class='pagination b-pagination']//li[@class='page-item active']//a/text()"
                            ).get()
                        )
                        other_pages = selector.xpath(
                            ".//ul[@class='pagination b-pagination']//li[@class='page-item']//a/text()"
                        ).getall()
                        other_pages = [int(page) for page in other_pages]
                        if (next_page := current_page + 1) in other_pages:
                            logger.info(f"Found another page, moving to page {next_page}")
                            page.click(
                                "//ul[@class='pagination b-pagination']//li[@class='page-item active']/"
                                "following-sibling::li//a"
                            )
                            page_content = page.content()
                            self.parse_page_content(page_content, url)
                        else:
                            next_page_available = False

                    browser.close()

            except Exception as e:
                logger.error(f"ERROR: {e}")

    def export_results(self):
        datestamp = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        save_dir = get_project_dir().joinpath("data", datestamp)
        save_dir.mkdir(exist_ok=True)
        with open(
            save_dir.joinpath(f"beertasting_{timestamp}.json"), "w", encoding="utf-8"
        ) as save_file:
            json.dump(self.scraped_products, save_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    beertasting_spider = BeertastingManualSpider()
    beertasting_spider.parse_urls()
    beertasting_spider.export_results()
