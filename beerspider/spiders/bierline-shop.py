from scrapy import Spider, Selector, Request
from loguru import logger
from beerspider.items import ProductItemLoader
from scrapy.shell import inspect_response


class BierlineSpider(Spider):
    name = "Bierlinie"
    main_url = "https://www.bierlinie-shop.de/"

    def start_requests(self):
        urls = [
            "https://www.bierlinie-shop.de/biersorten/abteibier",
            "https://www.bierlinie-shop.de/biersorten/ale",
            "https://www.bierlinie-shop.de/biersorten/alkoholfrei",
            "https://www.bierlinie-shop.de/biersorten/alt-biere",
            "https://www.bierlinie-shop.de/biersorten/craft-beer",
        ]

        # Add '?items=100' to retrieve 100 products per page and click between pages less
        urls = [f"{url}?items=100" for url in urls]

        for url in urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True},
            )

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        inspect_response(response, self)

        products = response.xpath("//article[contains(@class, 'cmp-product-thumb')]")

        for product in products:

            loader = ProductItemLoader(selector=product)

            style = response.url.split("/")[-1].replace("?items=100", "").replace("-", "").title()

            product_url = product.xpath(".//div[@class='thumb-image']//a/@href").get()
            product_url = f"{self.main_url}{product_url}"

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

            loader.add_xpath("name", ".//div[@class='thumb-image']//img/@title")
            loader.add_value("available", available)

            loader.add_value("product_url", product_url)
            loader.add_xpath("image_url", ".//div[@class='thumb-image']//img/@src")

            loader.add_xpath(
                "price_eur", ".//div[@class='price']//span[@class='price-value']/text()"
            )
            loader.add_value("volume_liter", volume)
            loader.add_value("price_eur_per_liter", price_per_liter)


