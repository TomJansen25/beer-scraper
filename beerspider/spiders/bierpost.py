from scrapy import Spider, Request
from datetime import datetime
from loguru import logger

from beerspider.items import ProductItemLoader


class BierPostSpider(Spider):
    """
    The Bierpost Spider used to crawl Beers from biershop.bierpost.com/de/
    """

    name = "bierpost"
    allowed_domains = ["biershop.bierpost.com"]
    main_url = "https://biershop.bierpost.com/de/"
    valid_delivery_color = "color:#0cc56d"
    invalid_delivery_color = "color:#ff0000"
    datestamp = datetime.now().strftime("%Y_%m_%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    def start_requests(self):
        urls = [
            "https://biershop.bierpost.com/de/abteibiere",
            "https://biershop.bierpost.com/de/amber",
            "https://biershop.bierpost.com/de/ale",
            "https://biershop.bierpost.com/de/alkoholfreie-getraenke",
            "https://biershop.bierpost.com/de/altbier",
            "https://biershop.bierpost.com/de/barleywine",
            "https://biershop.bierpost.com/de/barrel-aged",
            "https://biershop.bierpost.com/de/belgian-ale",
            "https://biershop.bierpost.com/de/belgian-strong-ale",
            "https://biershop.bierpost.com/de/berliner-weisse",
            "https://biershop.bierpost.com/de/biermischgetraenke",
            "https://biershop.bierpost.com/de/bio-bier",
            "https://biershop.bierpost.com/de/bitterbier",
            "https://biershop.bierpost.com/de/black-ipa",
            "https://biershop.bierpost.com/de/blond-blonde",
            "https://biershop.bierpost.com/de/bockbier-biersorten",
            "https://biershop.bierpost.com/de/brown-ale",
            "https://biershop.bierpost.com/de/bruin",
            "https://biershop.bierpost.com/de/dampfbier-steam-beer",
            "https://biershop.bierpost.com/de/dinkelbier",
            "https://biershop.bierpost.com/de/doppelbock",
            "https://biershop.bierpost.com/de/dubbel",
            "https://biershop.bierpost.com/de/dunkelbier",
            "https://biershop.bierpost.com/de/dry-hopping",
            "https://biershop.bierpost.com/de/eisbier-ice",
            "https://biershop.bierpost.com/de/english-strong-ale",
            "https://biershop.bierpost.com/de/esb-beer-extra-spezial-bitter",
            "https://biershop.bierpost.com/de/export-bier",
            "https://biershop.bierpost.com/de/fruchtbier",
            "https://biershop.bierpost.com/de/fruchtlambic",
            "https://biershop.bierpost.com/de/geuze-gueuze",
            "https://biershop.bierpost.com/de/glutenfreies-bier",
            "https://biershop.bierpost.com/de/gose",
            "https://biershop.bierpost.com/de/gruit-kraeuterbier",
            "https://biershop.bierpost.com/de/gruenhopfenbier",
            "https://biershop.bierpost.com/de/hanfbier",
            "https://biershop.bierpost.com/de/honigbier",
            "https://biershop.bierpost.com/de/hell",
            "https://biershop.bierpost.com/de/imperial-pils",
            "https://biershop.bierpost.com/de/imperial-porter",
            "https://biershop.bierpost.com/de/india-pale-ale-ipa",
            "https://biershop.bierpost.com/de/ipa-fruity",
            "https://biershop.bierpost.com/de/kellerbier",
            "https://biershop.bierpost.com/de/kirschbier-kaufen",
            "https://biershop.bierpost.com/de/klosterbiere-deutsch",
            "https://biershop.bierpost.com/de/koelsch",
            "https://biershop.bierpost.com/de/kuerbis-pumpkin",
            "https://biershop.bierpost.com/de/lagerbier",
            "https://biershop.bierpost.com/de/lager-dark",
            "https://biershop.bierpost.com/de/lite",
            "https://biershop.bierpost.com/de/lambic-bier",
            "https://biershop.bierpost.com/de/landbier-kaufen",
            "https://biershop.bierpost.com/de/malt-liquor",
            "https://biershop.bierpost.com/de/milk-stout",
            "https://biershop.bierpost.com/de/maerzen",
            "https://biershop.bierpost.com/de/new-england-ipa-neipa",
            "https://biershop.bierpost.com/de/oatmeal-hafer",
            "https://biershop.bierpost.com/de/old-ale",
            "https://biershop.bierpost.com/de/pale-ale-biersorten",
            "https://biershop.bierpost.com/de/pilsner",
            "https://biershop.bierpost.com/de/porter-bier",
            "https://biershop.bierpost.com/de/quadrupel-bier",
            "https://biershop.bierpost.com/de/radler-bier",
            "https://biershop.bierpost.com/de/roggenbier",
            "https://biershop.bierpost.com/de/rauchbier",
            "https://biershop.bierpost.com/de/redbeer-rotbier",
            "https://biershop.bierpost.com/de/saison-bier",
            "https://biershop.bierpost.com/de/sauer-bier-biersorten",
            "https://biershop.bierpost.com/de/scotch-ale-biersorten",
            "https://biershop.bierpost.com/de/session-ipa",
            "https://biershop.bierpost.com/de/schankbier",
            "https://biershop.bierpost.com/de/schwarzbier",
            "https://biershop.bierpost.com/de/schwarzbier-lieblich",
            "https://biershop.bierpost.com/de/single-hop",
            "https://biershop.bierpost.com/de/spezial-bier",
            "https://biershop.bierpost.com/de/steinbier",
            "https://biershop.bierpost.com/de/stout-bier",
            "https://biershop.bierpost.com/de/starkbier-strong-ale",
            "https://biershop.bierpost.com/de/trappistenbiere",
            "https://biershop.bierpost.com/de/tripel-triple",
            "https://biershop.bierpost.com/de/jahrgangsbier-vintage-ale",
            "https://biershop.bierpost.com/de/weissbier-weizen",
            "https://biershop.bierpost.com/de/weizenstarkbier",
            "https://biershop.bierpost.com/de/wit-white-ale-blanche",
            "https://biershop.bierpost.com/de/kellerbier-zwickel",
        ]
        urls = [f"{url}?s=120" for url in urls]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}!")

        products = response.css("article.art")
        num_products = len(products)
        logger.info(
            f"Found {num_products} products on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for product in products:
            try:
                loader = ProductItemLoader(selector=product)

                availability_color = product.xpath(
                    './/span[@class="delivery-time"]/@style'
                ).get()
                available = availability_color == self.valid_delivery_color

                loader.add_value("vendor", self.name)
                loader.add_xpath("brewery", './/div[@class="art-brand"]//span/text()')
                loader.add_value(
                    "style",
                    response.url.split("/")[-1]
                    .replace("?s=120", "")
                    .replace("-", " ")
                    .title(),
                )

                image_url = product.xpath(
                    ".//a[contains(@class, 'art-picture')]//img/@src"
                ).get()
                image_url = f"https:{image_url}"

                product_url = product.xpath(
                    ".//div[@class='art-picture-block']//a[contains(@class, 'art-picture')]/@href"
                ).get()
                loader.add_value(
                    "product_url", f'{self.main_url.replace("/de/", "")}{product_url}'
                )
                loader.add_value("image_url", image_url)

                loader.add_value("scraped_from_url", response.url)

                loader.add_xpath("name", './/h3[@class="art-name"]//a/@title')
                loader.add_xpath(
                    "description", './/div[@class="art-description"]/@title'
                )
                loader.add_value("available", available)

                full_volume = product.xpath('.//div[@class="art-pangv"]/@title').get()
                volume, price_per_liter = full_volume.split("(")
                volume = volume.replace("Inhalt:", "")
                price_per_liter = price_per_liter.replace("* / 1 l)", "")

                price_eur = product.xpath(
                    ".//span[contains(@class, 'art-price--offer')]/text()"
                ).get()
                on_sale = bool(price_eur)
                discount, original_price = None, None
                if on_sale:
                    original_price = product.xpath(
                        ".//span[@class='art-oldprice']/text()"
                    ).get()
                    discount = product.xpath(
                        ".//span[@class='badge badge-danger art-badge']/text()"
                    ).get()
                else:
                    price_eur = product.xpath(
                        ".//span[@class='art-price']/text()"
                    ).get()

                loader.add_value("price_eur", price_eur)
                loader.add_value("volume_liter", volume)
                loader.add_value("price_eur_per_liter", price_per_liter)

                loader.add_value("on_sale", on_sale)
                loader.add_value("original_price", original_price)
                loader.add_value("discount", discount)

                yield loader.load_item()
                # logger.info(loader.item.__dict__)
                success_counter += 1

            except Exception as e:
                self.logger.error(f"ERROR.. The following error occurred: {e}")
                logger.error(f"Error {e} occurred...")

        logger.info(
            f"Finished crawling {response.url}. Successfully crawled {success_counter} "
            f"out of {num_products} products!"
        )
