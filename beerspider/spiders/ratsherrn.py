import scrapy

from beerspider.items import ProductItemLoader


class RatsherrnSpider(scrapy.Spider):
    """Spider to crawl Ratsherrn beers sold directly through the Ratsherrn website"""

    name = "ratsherrn"
    main_url = "https://shop.ratsherrn.de/"

    def start_requests(self):
        urls = [
            "https://shop.ratsherrn.de/klassik-linie/",
            "https://shop.ratsherrn.de/organic-linie/",
            "https://shop.ratsherrn.de/kenner-linie/",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        page = response.url.split("/")[-2]

        self.logger.info(f"crawling {page}!")

        products = response.css("div.product--info")

        for product in products:
            loader = ProductItemLoader(selector=product)

            loader.add_value("vendor", self.name.capitalize())
            loader.add_value("brand", self.name.capitalize())
            loader.add_css("name", "a.product--title::attr(title)")
            loader.add_css("description", "div.product--description::text")
            loader.add_xpath("price", '//div[@class="product--price"]//span/text()')
            # loader.add_value('volume', product.css('div.price--unit').css('span::text').getall()[0])

            yield loader.load_item()
