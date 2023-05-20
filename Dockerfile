FROM python:3.10.10-bullseye

ENV PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.3.1

WORKDIR /app

RUN apt-get update
RUN apt-get install -y pkg-config

RUN pip install --no-cache-dir --upgrade pip
RUN pip install poetry==$POETRY_VERSION

RUN mkdir -p "$HOME"/beer-scraper
WORKDIR "$HOME"/beer-scraper

COPY ./beerspider "$HOME"/beer-scraper/beerspider
COPY ./cli "$HOME"/beer-scraper/cli
COPY Makefile "$HOME"/beer-scraper/
COPY run_scrapers.py "$HOME"/beer-scraper/
COPY scrapy.cfg "$HOME"/beer-scraper/
COPY README.md "$HOME"/beer-scraper/

COPY poetry.lock "$HOME"/beer-scraper/poetry.lock
COPY pyproject.toml "$HOME"/beer-scraper/pyproject.toml

RUN poetry config virtualenvs.create false
RUN poetry install --only main -vvv

# RUN PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright 
RUN poetry run playwright install --with-deps chromium

