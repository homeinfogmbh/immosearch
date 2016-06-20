"""Realtor and real estate filtering"""

from peewee import Model, IntegerField, BooleanField, ForeignKeyField,\
    CharField, BlobField

from homeinfo.peewee import MySQLDatabase
from homeinfo.crm import Customer

from .config import db

__all__ = ['Blacklist']

database = MySQLDatabase(
    db['DB'],
    host=db['HOST'],
    user=db['USER'],
    passwd=db['PASSWD'],
    closing=True)


class ImmoSearchModel(Model):
    """Basic database model for immosearch"""

    class Meta:
        database = database
        schema = database.database


class Blacklist(ImmoSearchModel):
    """List of users to apprehend ImmoSearch serving data for"""

    customer = ForeignKeyField(
        Customer, db_column='customer', related_name='immosearch')
