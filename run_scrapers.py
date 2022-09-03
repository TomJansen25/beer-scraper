from loguru import logger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor, verify_installed_reactor

from beerspider.spiders import (
    beertasting,
    beyondbeer,
    biermarket,
    bierothek,
    bierpost,
    bierselect,
    craftbeershop,
    meibier,
    ratsherrn,
)

if not verify_installed_reactor(
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
):
    logger.info("AsyncioSelectorReactor not installed yet and will be installed...")
    install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(beertasting.BeertastingSpider)
    process.crawl(beyondbeer.BeyondBeerSpider)
    process.crawl(biermarket.BiermarketSpider)
    process.crawl(bierothek.BierothekSpider)
    process.crawl(bierpost.BierPostSpider)
    process.crawl(bierselect.BierSelectSpider)
    process.crawl(craftbeershop.CraftbeerShopSpider)
    process.crawl(meibier.MeibierSpider)
    process.crawl(ratsherrn.RatsherrnSpider)
    process.start()
