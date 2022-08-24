from __future__ import annotations

import re

import numpy as np
from itemloaders.processors import Identity, MapCompose, TakeFirst
from price_parser import Price
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader

NUMBER_PATTERN = r"[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+"


def remove_special_characters(text: str) -> str:
    """
    Removes special characters from a string
    :param text: string to process
    :return: processed string
    """
    text = text.strip()
    return text


def percentage_str_to_number(percentage_str: str) -> float | int:
    """

    :param percentage_str:
    :return:
    """
    percentage_str = percentage_str.lower().replace("%", "")
    percentage = abs(float(re.search(NUMBER_PATTERN, percentage_str)[0]))
    return percentage


def volume_str_to_float(volume_str: str) -> float:
    """

    :param volume_str:
    :return:
    """
    volume_str = volume_str.lower().replace(",", ".")
    volume = float(re.search(NUMBER_PATTERN, volume_str)[0])

    if "ml" in volume_str:
        volume_liter = volume / 1000
    elif "cl" in volume_str:
        volume_liter = volume / 100
    elif "dl" in volume_str:
        volume_liter = volume / 10
    elif "l" in volume_str or "ltr" in volume_str:
        volume_liter = volume
    else:
        volume_liter = volume

    return np.round(volume_liter, 2)


def price_str_to_float(price_str: str) -> float:
    """

    :param price_str:
    :return:
    """
    price = Price.fromstring(price_str)
    return price.amount_float


def price_volume_str_to_float(price_str: str) -> float:
    """

    :param price_str:
    :return:
    """
    price_str = price_str.lower()
    price = Price.fromstring(price_str)

    if "pro 100 ml" in price_str or "(100 ml)" in price_str:
        price = price.amount_float * 10
    elif (
        "pro liter" in price_str
        or "pro l" in price_str
        or "liter" in price_str
        or "/ltr" in price_str
    ):
        price = price.amount_float
    else:
        price = price.amount_float

    return np.round(price, 2)


class ProductItem(Item):
    """
    The ProductItem contains all the Fields
    """

    vendor = Field()
    brewery = Field()
    style = Field()

    product_url = Field()
    image_url = Field()
    scraped_from_url = Field()

    name = Field()
    description = Field()
    available = Field(input_processor=Identity())

    price_eur = Field(
        input_processor=MapCompose(remove_special_characters, price_str_to_float)
    )
    volume_liter = Field(input_processor=MapCompose(volume_str_to_float))
    price_eur_per_liter = Field(
        input_processor=MapCompose(remove_special_characters, price_volume_str_to_float)
    )

    on_sale = Field(input_processor=Identity())
    original_price = Field(
        input_processor=MapCompose(remove_special_characters, price_str_to_float)
    )
    discount = Field(
        input_processor=MapCompose(remove_special_characters, percentage_str_to_number)
    )


class ProductItemLoader(ItemLoader):
    default_item_class = ProductItem

    default_input_processor = MapCompose(remove_special_characters)
    default_output_processor = TakeFirst()
