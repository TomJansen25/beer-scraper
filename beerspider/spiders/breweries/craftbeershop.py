from datetime import datetime

from loguru import logger
from scrapy import Request, Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class CraftbeerShopBrewerySpider(CrawlSpider):
    """
    Craftbeer Shop Spider Class
    """

    name = "craftbeer_shop_breweries"
    allowed_domains = ["craftbeer-shop.com"]
    main_url = "https://www.craftbeer-shop.com/"
    start_urls = ["https://www.craftbeer-shop.com/"]
    datestamp = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    rules = (
        Rule(
            LinkExtractor(allow=("Brauereien/", "brauereien/")),
            callback="parse",
            follow=True,
        ),
    )

    def parse(self, response, **kwargs):
        logger.info(f"Crawling {response.url}...")

        breweries = response.xpath("//div[contains(@class, 'subcategory-card')]")
        num_breweries = len(breweries)
        logger.info(
            f"Found {num_breweries} breweries on page {response.url}, starting to crawl..."
        )
        success_counter = 0

        for brewery in breweries:

            name = brewery.css("a.subcategory-card__title::text").get()
            country = response.url.split("/")[-1]

            icon_url = brewery.xpath(
                ".//div[contains(@class, 'subcategory-card__image')]//img/@data-src"
            ).get()
            scraped_from_url = response.url
            logger.info(name, country, icon_url, scraped_from_url)

            yield {
                "name": name,
                "country": country,
                "icon_url": icon_url,
                "scraped_from_url": scraped_from_url,
            }
            success_counter += 1
