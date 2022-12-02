FROM ubuntu:20.04

RUN apt update && apt install -y python3.9 python3.9-dev python3.9-distutils
RUN apt update && apt install -y curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN apt update && apt install -y pkg-config build-essential

# https://python-poetry.org/docs/master/#installation
ENV POETRY_VERSION=1.2.1
# Use Poetry currently only to export requirements from pyproject.toml, and thus easy install with pip further below is enough
# RUN curl -sSL https://install.python-poetry.org | python3.9 - --version "$POETRY_VERSION"

RUN python3.9 -m pip install poetry==$POETRY_VERSION

RUN mkdir -p "$HOME"/beer-scraper
WORKDIR "$HOME"/beer-scraper

COPY poetry.lock "$HOME"/beer-scraper/poetry.lock
COPY pyproject.toml "$HOME"/beer-scraper/pyproject.toml
RUN poetry config virtualenvs.in-project true --local
# RUN poetry install --no-dev
RUN poetry export --without-hashes -f requirements.txt --output requirements.txt
RUN python3.9 -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN playwright install && playwright install-deps

COPY ./beerspider "$HOME"/beer-scraper/beerspider
COPY Makefile "$HOME"/beer-scraper
COPY run_scrapers.py "$HOME"/beer-scraper
COPY scrapy.cfg "$HOME"/beer-scraper
