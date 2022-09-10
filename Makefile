SCRAPER_CONTAINER_NAME=beer-scraper/scraper


.PHONY: python-format
python-format:
	poetry run isort .
	poetry run black .


.PHONY: scrape-all
scrape-all:
	poetry shell && python ./run_scrapers.py


## --------------------------- DOCKER COMMANDS --------------------------- ##

.PHONY: scrape-container-start
start-container:
	sudo docker run -dit -v /mnt/c/Users/tomja/Desktop/Programming/beer-scraper/beer_dev.db:/beer-scraper/beer_dev.db --name $(SCRAPER_CONTAINER_NAME) beer-scraper
	sudo docker exec -it $(SCRAPER_CONTAINER_NAME) bash

.PHONY: scrape-container-delete
scrape-container-delete:
	sudo docker stop $(SCRAPER_CONTAINER_NAME)
	sudo docker rm $(SCRAPER_CONTAINER_NAME)
