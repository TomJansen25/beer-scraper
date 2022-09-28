from loguru import logger
from datetime import datetime
from scrapy import Request, Spider, Selector
from scrapy.shell import inspect_response
from scrapy.utils.reactor import install_reactor, verify_installed_reactor
from scrapy_playwright.handler import Page
from scrapy_playwright.page import PageMethod

from beerspider.items import ProductItemLoader, volume_str_to_float


class FlaschenpostSpider(Spider):
    name = "flaschenpost"
    allowed_domains = ["flaschenpost.de"]
    main_url = "https://www.flaschenpost.de/"
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    success_counter = 0

    def __init__(self, **kwargs):
        if not verify_installed_reactor(
                "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
        ):
            logger.info("AsyncioSelectorReactor not installed yet and will be installed...")
            install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

        super().__init__(**kwargs)

    def start_requests(self):
        urls = [
            "https://www.flaschenpost.de/bier/alkoholfrei",
            # "https://www.flaschenpost.de/bier/helles",
            # "https://www.flaschenpost.de/bier/internationale-biere",
            # "https://www.flaschenpost.de/bier/koelsch",
            # "https://www.flaschenpost.de/bier/land-kellerbier",
            # "https://www.flaschenpost.de/bier/malzbier",
            # "https://www.flaschenpost.de/bier/pils",
            # "https://www.flaschenpost.de/bier/radler-biermix",
            # "https://www.flaschenpost.de/bier/spezialitaeten",
            # "https://www.flaschenpost.de/bier/weizenbier",
        ]

        for url in urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                ),
            )

    async def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        page: Page = response.meta["playwright_page"]

        await page.locator("//div[@class='zipcode_input_component']//input").fill("20251")
        await page.wait_for_selector(
            "//button[@class='fp_button fp_button_primary fp_button_large']"
        )
        await page.click("//button[@class='fp_button fp_button_primary fp_button_large']")
        await page.wait_for_selector("//div[@class='fp_product']")
        await page.wait_for_timeout(5000)

        page_content = await page.content()
        selector = Selector(text=page_content)

        products = selector.xpath("//div[@class='fp_product']")
        products_on_sale = selector.xpath("//div[@class='fp_product isOffer']")
        num_products = len(products + products_on_sale)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        self.success_counter = 0

        for product in products:
            self.parse_product(product=product, url=response.url)

        for product in products_on_sale:
            self.parse_product(product=product, url=response.url, on_sale=True)

        logger.info(
            f"Finished crawling {response.url}. "
            f"Successfully crawled {self.success_counter} out of {num_products} products!"
        )

    async def parse_product(self, product: Selector, url: str, on_sale: bool = False):
        """

        :param product:
        :param url:
        :param on_sale:
        """
        try:
            print("parsing...")
            style = url.split("/")[-1].replace("-", " ").title()

            image_url = product.css("a.fp_product_image").attrib.get("href")
            image_url = f"{self.main_url[:-1]}{image_url}"

            original_price = None

            varieties = product.xpath(
                ".//div[contains(@class, 'fp_article bottleTypeExists')]"
            )
            print(str(varieties))

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
                print(price_eur)

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
                print(price_per_liter)

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", str(volume))
                loader.add_value("price_eur_per_liter", price_per_liter)

                if on_sale:
                    original_price = variety.css(
                        "div.fp_article_price_stroked::text"
                    ).get()

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)

                yield loader.load_item()
                logger.info(loader.item.__dict__)
                self.success_counter += 1

        except Exception as e:
            self.logger.error(f"ERROR.. The following error occurred: {e}")
            logger.error(f"Error {e} occurred...")
