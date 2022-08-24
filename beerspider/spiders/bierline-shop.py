import scrapy

from beerspider.items import ProductItemLoader


class BierLineSpider(scrapy.Spider):
    name = "Bierlinie"
    main_url = "https://www.bierlinie-shop.de/"

    def start_requests(self):
        urls = [
            "https://www.bierlinie-shop.de/biersorten/alkoholfreie-getraenke",
            "https://www.bierlinie-shop.de/biersorten/ale",
            "https://www.bierlinie-shop.de/biersorten/craft-beer",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        print(f"Crawling {response.url}!")

        products = response.xpath("//li[@class='mb-4 col-12 col-sm-6 col-md-3']")

        for product in products:
            print(product)
