# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#
# useful for handling different item types with a single interface
from datetime import datetime

from itemadapter import ItemAdapter
from loguru import logger
from scrapy import Spider
from sqlalchemy.orm import sessionmaker

from beerspider.database.models import Product
from beerspider.database.utils import create_table, db_connect
from beerspider.items import ProductItem


class BeerspiderPipeline:
    """
    Pipeline to write results to a database
    """

    def __init__(self):
        """
        Initializes database_ connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item: ProductItem, spider: Spider):
        session = self.Session()

        product = Product()

        product.name = item.get("name")
        product.vendor = item.get("vendor")
        product.brewery = item.get("brewery")
        product.style = item.get("style")

        product.product_url = item.get("product_url")
        product.scraped_from_url = item.get("scraped_from_url")
        product.image_url = item.get("image_url")
        product.scrape_datetime = datetime.now()
        product.available = item.get("available")

        product.description = item.get("description")
        product.price_eur = item.get("price_eur")
        product.volume_liter = item.get("volume_liter")
        product.price_eur_per_liter = item.get("price_eur_per_liter")

        product.on_sale = item.get("on_sale")
        product.original_price = item.get("original_price")
        product.discount = item.get("discount")

        try:
            session.add(product)
            session.commit()

        except Exception as e:
            session.rollback()
            logger.info(f"An error occurred: {e}")
            raise Exception(e)

        finally:
            session.close()

        return item
