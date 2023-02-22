from beerspider.spiders.beers.rewe_manual import ReweShopSpider
from beerspider.spiders.beers.flaschenpost_manual import FlaschenpostManualSpider

if __name__ == "__main__":
    # rewe_spider = ReweShopSpider(scrape_headless=False)
    # rewe_spider.parse_urls()

    fp_spider = FlaschenpostManualSpider(scrape_headless=False)
    fp_spider.parse_urls()
    fp_spider.export_results()
