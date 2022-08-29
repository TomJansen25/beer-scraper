from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from beerspider.spiders import (
    beertasting,
    beyondbeer,
    biermarket,
    bierothek,
    bierpost,
    bierselect,
    craftbeershop,
)

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(beyondbeer.BeyondBeerSpider)
process.crawl(bierothek.BierothekSpider)
process.crawl(bierpost.BierPostSpider)
process.crawl(biermarket.BiermarketSpider)
process.crawl(bierselect.BierSelectSpider)
process.crawl(craftbeershop.CraftbeerShopSpider)
process.crawl(beertasting.BeertastingSpider)
process.start()
