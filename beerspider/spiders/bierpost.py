import scrapy

from beerspider.items import ProductItemLoader


class BierPostSpider(scrapy.Spider):
    """
    The Bierpost Spider used to crawl Beers from biershop.bierpost.com/de/
    """

    name = "BierPost"
    allowed_domains = ["biershop.bierpost.com"]
    main_url = "https://biershop.bierpost.com/de/"
    valid_delivery_color = "color:#15d213"
    invalid_delivery_color = "color:#ff0000"

    def start_requests(self):
        urls = [
            "https://biershop.bierpost.com/de/hell",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        print(f"Crawling {response.url}!")

        products = response.css("article.art")

        for product in products:
            loader = ProductItemLoader(selector=product)

            if (
                product.xpath('.//span[@class="delivery-time"]/@style').get()
                == self.invalid_delivery_color
            ):
                continue

            loader.add_value("vendor", self.name)
            loader.add_xpath("brewery", './/div[@class="art-brand"]//span/text()')
            loader.add_value("style", response.url.split("/")[-1])

            product_url = product.xpath(
                './/a[contains(@class, "art-picture")]/@href'
            ).get()
            loader.add_value(
                "product_url", f'{self.main_url.replace("/de/", "")}{product_url}'
            )
            loader.add_xpath(
                "image_url", './/a[contains(@class, "art-picture")]//img/@src'
            )

            loader.add_value("scraped_from_url", response.url)

            loader.add_xpath("name", './/h3[@class="art-name"]//a/@title')
            loader.add_xpath("description", './/div[@class="art-description"]/@title')

            full_volume = product.xpath('.//div[@class="art-pangv"]/@title').get()

            loader.add_xpath("price_eur", './/span[@class="art-price"]/text()')
            loader.add_value("volume_liter", "")
            loader.add_value("price_eur_per_liter", "")

            loader.add_value("on_sale", on_sale)
            loader.add_xpath(
                "original_price", './/div[contains(@class, "original-price")]/text()'
            )
