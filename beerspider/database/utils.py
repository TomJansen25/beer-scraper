from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from beerspider.database.models import Base


def db_connect():
    """
    Performs database_ connection using database_ settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)
