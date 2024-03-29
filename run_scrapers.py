from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from beerspider.spiders.beers import (
    beyondbeer,
    bierdeluxe,
    bierkaufen,
    bierlinie,
    biermarket,
    bierothek,
    bierpost,
    bierselect,
    craftbeershop,
    hiergibtsbier,
    holycraft,
    meibier,
    ratsherrn,
)
from beerspider.spiders.beers.beertasting_manual import BeertastingManualSpider
from beerspider.spiders.beers.bierlinie_manual import BierlinieManualSpider
from beerspider.spiders.beers.meibier_manual import MeibierManuelSpider

# from beerspider.spiders.beers.flaschenpost_manual import FlaschenpostManualSpider

if __name__ == "__main__":
    beertasting_spider = BeertastingManualSpider(
        scrape_headless=True, scrape_from_germany=True
    )
    beertasting_spider.parse_urls()
    beertasting_spider.export_results()

    bierlinie_spider = BierlinieManualSpider(scrape_headless=True)
    bierlinie_spider.parse_urls()
    bierlinie_spider.export_results()

    meibier_spider = MeibierManuelSpider(scrape_headless=True)
    meibier_spider.parse_urls()
    meibier_spider.export_results()

    # flaschenpost_spider = FlaschenpostManualSpider(scrape_headless=True)
    # flaschenpost_spider.parse_urls()
    # flaschenpost_spider.export_results()

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(beyondbeer.BeyondBeerSpider)
    # process.crawl(bierdeluxe.BierDeluxeSpider)
    process.crawl(bierkaufen.BierKaufenSpider)
    # process.crawl(bierlinie.BierlineSpider)
    process.crawl(biermarket.BiermarketSpider)
    process.crawl(bierothek.BierothekSpider)
    process.crawl(bierpost.BierPostSpider)
    process.crawl(bierselect.BierSelectSpider)
    process.crawl(craftbeershop.CraftbeerShopSpider)
    process.crawl(hiergibtsbier.HiergibtsbierSpider)
    process.crawl(holycraft.HolyCraftSpider)
    # process.crawl(meibier.MeibierSpider)
    process.crawl(ratsherrn.RatsherrnSpider)
    process.start()
