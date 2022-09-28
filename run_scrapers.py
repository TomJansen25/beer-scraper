from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from beerspider.spiders import (
    beertasting,
    beyondbeer,
    bierline,
    biermarket,
    bierothek,
    bierpost,
    bierselect,
    craftbeershop,
    meibier,
    ratsherrn,
)

if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    # process.crawl(beertasting.BeertastingSpider)
    process.crawl(beyondbeer.BeyondBeerSpider)
    process.crawl(bierline.BierlineSpider)
    process.crawl(biermarket.BiermarketSpider)
    process.crawl(bierothek.BierothekSpider)
    process.crawl(bierpost.BierPostSpider)
    process.crawl(bierselect.BierSelectSpider)
    process.crawl(craftbeershop.CraftbeerShopSpider)
    process.crawl(meibier.MeibierSpider)
    process.crawl(ratsherrn.RatsherrnSpider)
    process.start()
