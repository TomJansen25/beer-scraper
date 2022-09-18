from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Brewery(Base):
    __tablename__ = "brewery"

    id = Column(Integer, primary_key=True)

    name = Column("name", String, nullable=False)
    country = Column("country", String, nullable=True)

    url = Column("url", String, nullable=True)
    icon_url = Column("image_url", String, nullable=True)

    scraped_from_url = Column("scraped_from_url", String, nullable=False)
    scrape_datetime = Column("scrape_datetime", DateTime, nullable=False)


class Vendor(Base):
    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    url = Column("url", String, nullable=False)


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)

    vendor = Column("vendor", String, nullable=False)
    brewery = Column("brewery", String, nullable=True)
    style = Column("style", String, nullable=True)

    product_url = Column("product_url", String, nullable=False)
    image_url = Column("image_url", String, nullable=True)

    scraped_from_url = Column("scraped_from_url", String, nullable=False)
    scrape_datetime = Column("scrape_datetime", DateTime, nullable=False)

    name = Column("name", String, nullable=False)
    description = Column("description", Text, nullable=True)
    available = Column("available", Boolean, nullable=False)

    price_eur = Column("price_eur", Float, nullable=True)
    volume_liter = Column("volume_liter", Float, nullable=True)
    price_eur_per_liter = Column("price_eur_per_liter", Float, nullable=True)

    on_sale = Column("on_sale", Boolean, nullable=False)
    original_price = Column("original_price", Float, nullable=True)
    discount = Column("discount", Float, nullable=True)
