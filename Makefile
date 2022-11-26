SCRAPER_IMAGE_NAME=beer-scraper/scraper
SCRAPER_CONTAINER_NAME=beer-scraper
PROJECT_DIR=$HOME/


.PHONY: python-format
python-format:
	poetry run isort .
	poetry run black .


.PHONY: scrape-all
scrape-all:
	poetry shell && python ./run_scrapers.py


## --------------------------- DOCKER COMMANDS --------------------------- ##

.PHONY: scraper-docker-build
scraper-docker-build:
	docker build -f Dockerfile -t $(SCRAPER_IMAGE_NAME) .

.PHONY: scraper-docker-start
scraper-docker-start:
	docker run -dit --name $(SCRAPER_CONTAINER_NAME) $(SCRAPER_IMAGE_NAME):latest
	docker exec -it $(SCRAPER_CONTAINER_NAME) bash

.PHONY: scraper-docker-delete
scraper-docker-delete:
	docker rm --force $(SCRAPER_CONTAINER_NAME)
