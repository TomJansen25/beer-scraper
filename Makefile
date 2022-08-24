.PHONY: scrape-all
scrape-all:
	poetry shell && python ./run_scrapers.py


.PHONY: python-format
python-format:
	poetry run isort .
	poetry run black .
