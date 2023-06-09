import typer

from beerspider.spiders.beers.beertasting_manual import BeertastingManualSpider
from beerspider.spiders.beers.bierlinie_manual import BierlinieManualSpider
from beerspider.spiders.beers.flaschenpost_manual import FlaschenpostManualSpider
from beerspider.spiders.beers.rewe_manual import ReweShopSpider

app = typer.Typer(name="beer-scraper-cli", no_args_is_help=True)


@app.command()
def run_beertasting_spider(headless: bool = True, scrape_from_germany: bool = True):
    beertasting_spider = BeertastingManualSpider(
        scrape_headless=headless, scrape_from_germany=scrape_from_germany
    )
    beertasting_spider.parse_urls()
    beertasting_spider.export_results()


@app.command()
def run_bierlinie_spider(headless: bool = True):
    bierlinie_spider = BierlinieManualSpider(scrape_headless=headless)
    bierlinie_spider.parse_urls()
    bierlinie_spider.export_results()


@app.command()
def run_flaschenpost_spider(headless: bool = True):
    flaschenpost_spider = FlaschenpostManualSpider(scrape_headless=headless)
    flaschenpost_spider.parse_urls()
    flaschenpost_spider.export_results()
