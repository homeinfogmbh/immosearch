"""Realtor and real estate filtering."""

from peewee import Model, ForeignKeyField

from peeweeplus import MySQLDatabase
from homeinfo.crm import Customer

from .config import CONFIG

__all__ = ['Blacklist']

DATABASE = MySQLDatabase(
    CONFIG['db']['DB'],
    host=CONFIG['db']['HOST'],
    user=CONFIG['db']['USER'],
    passwd=CONFIG['db']['PASSWD'],
    closing=True)


class ImmoSearchModel(Model):
    """Basic database model for immosearch."""

    class Meta:
        database = DATABASE
        schema = DATABASE.database


class Blacklist(ImmoSearchModel):
    """List of users to apprehend ImmoSearch serving data for."""

    customer = ForeignKeyField(
        Customer, db_column='customer', related_name='immosearch')
