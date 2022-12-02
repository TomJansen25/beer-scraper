from beerspider.spiders.beers.rewe_manual import ReweShopSpider

if __name__ == "__main__":
    rewe_spider = ReweShopSpider(scrape_headless=False)
    rewe_spider.parse_urls()
