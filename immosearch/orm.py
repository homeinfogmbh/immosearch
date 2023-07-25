"""Realtor and real estate filtering."""

from peewee import Model, ForeignKeyField

from mdb import Customer
from peeweeplus import MySQLDatabaseProxy


__all__ = ["Blacklist"]


DATABASE = MySQLDatabaseProxy("immosearch")


class ImmoSearchModel(Model):
    """Basic database model for immosearch."""

    class Meta:  # pylint: disable=C0111,R0903
        database = DATABASE
        schema = DATABASE.database


class Blacklist(ImmoSearchModel):
    """List of users to apprehend ImmoSearch serving data for."""

    customer = ForeignKeyField(
        Customer, column_name="customer", related_name="immosearch", lazy_load=False
    )
