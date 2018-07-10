"""Realtor and real estate filtering."""

from peewee import Model, ForeignKeyField

from mdb import Customer
from peeweeplus import MySQLDatabase

from .config import CONFIG

__all__ = ['Blacklist']


DATABASE = MySQLDatabase.from_config(CONFIG['db'])


class ImmoSearchModel(Model):
    """Basic database model for immosearch."""

    class Meta:
        database = DATABASE
        schema = DATABASE.database


class Blacklist(ImmoSearchModel):
    """List of users to apprehend ImmoSearch serving data for."""

    customer = ForeignKeyField(
        Customer, column_name='customer', related_name='immosearch')
