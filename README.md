# Beer Scraper
Project to scrape German beer vendors finding the best deals and cheapest options!

# Development

- Poetry
- Scrapy
- Unix system required (WSL/Linux/MacOS)
  - Usage of playwright for dynamic websites is only supported in Unix systems

## Vendor websites:
* [Beertasting](https://www.beertasting.com/de-de) - __Done__
* [Beerwulf](https://www.beerwulf.com/de-de/) - __To Do__
* [Beyond Beer](https://www.beyondbeer.de/) - __Done__
* [Bierlinie](https://www.bierlinie-shop.de/) - __Done__
* [Biermarket](https://www.biermarket.de/) - __Done__
* [Bierothek](https://bierothek.de/) - __Done__
* [BierPost](https://biershop.bierpost.com/de) - __In progress__
* [BierSelect](https://bierselect.de/) - __Done__
* [Craftbeer Shop](https://www.craftbeer-shop.com/) - __Done__
* [Flaschenpost](https://www.flaschenpost.de/) - __Semi Done__
* [Hier gibt's Bier](https://www.hier-gibts-bier.de/de/) - __To Do__
* [Holy Craft](https://holycraft.de/) - __Done__
* [Meibier](https://www.meibier.de/) - __Done__
* [Mein Biershop](https://www.mein-biershop.de/de/) - __To Do__
* [Mr Hop](https://www.misterhop.de/) - __To Do__ 
* [Ratsherrn]() - __Done__
* [REWE]() - __On Hold__

### Run scrapers:
```shell
cd $HOME/beer-scraper/
make scrape-all
```

or:

```shell
> cd $HOME/beer-scraper/
> poetry shell
> scrapy crawl "beyond_beer"
> scrapy crawl "bierothek" 
> scrapy crawl "craftbeer_shop"   
```


### Testing around with playwright

```shell
# OPEN WSL SHELL!
cd $HOME/../mnt/c/Users/tomja/Desktop/Programming/beer-scraper
```

### Useful Links:

* [Burplist GitHub](https://github.com/ngshiheng/burplist)
* [Scrapy BigQuery Pipeline](https://github.com/8W9aG/scrapy-bigquery/blob/main/bigquerypipeline/pipelines.py)
* [Selfmade Pipeline](https://github.com/djchie/webreg_scrapy/tree/master/webreg_scrapy)
* [Scraper Heroku Deployment](https://medium.com/geekculture/how-to-deploy-python-scrapy-spiders-for-free-on-cloud-154536ce5e89)
* 