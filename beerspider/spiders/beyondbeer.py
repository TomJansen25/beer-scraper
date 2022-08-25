import scrapy
from loguru import logger

from beerspider.items import ProductItemLoader


class BeyondBeerSpider(scrapy.Spider):
    name = "Beyond Beer"
    main_url = "https://www.beyondbeer.de/"

    def start_requests(self):
        urls = [
            "https://www.beyondbeer.de/alkoholfreies-craft-beer/",
            "https://www.beyondbeer.de/altbier-koelsch/",
            "https://www.beyondbeer.de/barley-wine/",
            "https://www.beyondbeer.de/belgian-ale/",
            "https://www.beyondbeer.de/berliner-weisse/",
            "https://www.beyondbeer.de/brown-ale/",
            "https://www.beyondbeer.de/cider/",
            "https://www.beyondbeer.de/hefeweizen/",
            "https://www.beyondbeer.de/helles/",
            "https://www.beyondbeer.de/ipa/",
            "https://www.beyondbeer.de/lager-bier/",
            "https://www.beyondbeer.de/pale-ale/",
            "https://www.beyondbeer.de/pilsner-bier/",
            "https://www.beyondbeer.de/porter-stout/",
            "https://www.beyondbeer.de/red-ale/",
            "https://www.beyondbeer.de/saison-farmhouse-ale/",
            "https://www.beyondbeer.de/sour-ale-wild-ale/",
            "https://www.beyondbeer.de/andere-bierstile/",
            "https://www.beyondbeer.de/sale/",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}...")

        products = response.xpath('//div[@class="product--box box--minimal"]')
        logger.info(f"Found {len(products)} products on page {response.url}, starting to crawl...")
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                images = product.xpath(
                    './/div[@class="product--info"]//a//span//span//img/@srcset'
                ).get()
                image_url = images.split(", ")[0] if images else None

                availability = product.xpath(".//span[@class='buy-btn--cart-add']")
                available = bool(availability)

                original_price = product.css("span.price--discount::text").get()
                on_sale = bool(original_price)

                loader.add_value("vendor", self.name)
                loader.add_xpath("brewery", './/h3[@class="supplier--name"]/text()')
                loader.add_css("style", "h2.product--style::text")

                loader.add_xpath("product_url", './/div[@class="product--info"]//a/@href')
                loader.add_value("image_url", image_url)

                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath("name", './/a[@class="product--title"]/@title')
                loader.add_value("available", available)

                loader.add_css(
                    "price_eur", "div.product--price > span.price--default::text"
                )
                loader.add_xpath(
                    "volume_liter", './/div[@class="price--unit"]//span[2]/text()'
                )
                loader.add_xpath(
                    "price_eur_per_liter", './/div[@class="price--unit"]//span[3]/text()'
                )

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)

                yield loader.load_item()
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} products!"
        )

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.css("a.paging--next").attrib.get("href")
        if next_page is not None:
            next_page_number = next_page.split("?")[1]
            current_page = response.url.split("?")[0]
            next_page = f"{current_page}?{next_page_number}"

            logger.info(f"Found another page, moving to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
