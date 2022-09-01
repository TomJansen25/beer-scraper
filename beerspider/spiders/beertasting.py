from loguru import logger
from scrapy import Request, Selector, Spider
from scrapy.shell import inspect_response
from scrapy.utils.reactor import install_reactor, verify_installed_reactor
from scrapy_playwright.handler import Page
from scrapy_playwright.page import PageMethod

from beerspider.items import ProductItemLoader, volume_str_to_float

if not verify_installed_reactor(
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
):
    logger.info("AsyncioSelectorReactor not installed yet and will be installed...")
    install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")


class BeertastingSpider(Spider):
    name = "Beertasting"
    main_url = "https://www.beertasting.com/"

    def start_requests(self):
        urls = [
            "https://www.beertasting.com/de-de/biere/ale-angloamerikanisch",
            "https://www.beertasting.com/de-de/biere/ale-belgisch",
            "https://www.beertasting.com/de-de/biere/alkoholfrei",
            "https://www.beertasting.com/de-de/biere/biermischgetranke",
            "https://www.beertasting.com/de-de/biere/bock",
            "https://www.beertasting.com/de-de/biere/cider",
            "https://www.beertasting.com/de-de/biere/dunkles-lager",
            "https://www.beertasting.com/de-de/biere/helles-lager",
            "https://www.beertasting.com/de-de/biere/india-pale-ale",
            "https://www.beertasting.com/de-de/biere/kreativbier",
            "https://www.beertasting.com/de-de/biere/nachreifung",
            "https://www.beertasting.com/de-de/biere/obergarige-leichtbiere",
            "https://www.beertasting.com/de-de/biere/porter-stout",
            "https://www.beertasting.com/de-de/biere/sauergarung",
            "https://www.beertasting.com/de-de/biere/weissbier",
            "https://www.beertasting.com/de-de/glutenfrei",
        ]

        for url in urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod(
                            method="click",
                            selector="//div[contains(@class, 'bts-per-page-select')]//button",
                        ),
                        PageMethod(method="click", selector="//a[@id='bs-select-1-2']"),
                    ],
                ),
                errback=self.errback_close_page,
            )

    async def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        page: Page = response.meta["playwright_page"]
        page_content = await page.content()
        playwright_selector = Selector(text=page_content)

        products = playwright_selector.xpath(
            "//div[contains(@class, 'bts-product-item--beer')]"
        )
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )

        # products = response.xpath("//div[contains(@class, 'bts-product-item--beer')]")
        # logger.info(f"Found {len(products)} products on page, starting to crawl...")

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
                    )
                    discount = discount_badge.css("span.item-label::text")
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

                loader.add_value("scraped_from_url", response.url)

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
                    f".//p[@class='bts-product-item__price-information']//"
                    f"span[@class='js-base-price']/text()",
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)
                loader.add_value("discount", discount)

                yield loader.load_item()
                # logger.info(loader.item.__dict__)
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        current_page = int(
            response.xpath(
                ".//ul[@class='pagination b-pagination']//li[@class='page-item active']//a/text()"
            ).get()
        )

        logger.info(
            f"Finished crawling page {current_page} of {response.url}! "
            f"Successfully crawled {success_counter} out of {num_products} products!"
        )

        other_pages: list[str] = response.xpath(
            ".//ul[@class='pagination b-pagination']//li[@class='page-item']//a/text()"
        ).getall()
        other_page_numbers = [int(str(page)) for page in other_pages]

        if (next_page := current_page + 1) in other_page_numbers:
            logger.info(f"Found another page, moving to page {next_page}")
            yield Request(
                url=response.url,
                callback=self.parse,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod(
                            method="click",
                            selector="//ul[@class='pagination b-pagination']//li[@class='page-item "
                            "active']/following-sibling::li//a",
                        ),
                    ],
                ),
            )

    async def errback_close_page(self, failure):
        logger.error(f"The following error occurred: {failure}")
        page = failure.request.meta["playwright_page"]
        await page.close()
