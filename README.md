# Beer Scraper
Project to scrape German beer vendors finding the best deals and cheapest options!

# Development

- Poetry
- Scrapy
- Unix system required (WSL/Linux/MacOS)
  - Usage of playwright for dynamic websites is only supported in Unix systems

## Vendor websites:
* [Beyond Beer]() - __Done__
* [Craftbeer Shop]() - __Done__
* [BierSelect]() - __Done__
* [Bierothek]() - __Done__
* [Ratsherrn]() - __In progress__
* [Biermarket]() - __Done__
* [BierPost]() - __In progress__
* [Bierlinie](https://www.bierlinie-shop.de/) - __On hold__
* [Beertasting](https://www.beertasting.com/de-de) - __In progress__


### Current TODOs:
* Implement playwright/scrapy_playwright for dynamic content
* Fix craftbeer-shop.com paging (no longer through link but dynamic link click)
* ...


### Run scrapers:
```shell
cd $HOME/beer-scraper/
poetry shell
python ./run_scrapers.py
```

or:

```shell
> cd $HOME/beer-scraper/
> poetry shell
> scrapy crawl "BierSelect"
> scrapy crawl "Beyond Beer"
> scrapy crawl "Biermarket"
> scrapy crawl "Bierothek" 
> scrapy crawl "Craftbeer Shop"   
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