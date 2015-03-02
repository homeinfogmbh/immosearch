"""Realtor and real estate filtering"""

from peewee import MySQLDatabase, Model, IntegerField, BooleanField,\
    ForeignKeyField, CharField
from homeinfo.crm import Customer
from .config import db
from homeinfolib.db import create

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['ImmoSearchUser']

database = MySQLDatabase(db['DB'], host=db['HOST'], user=db['USER'],
                         passwd=db['PASSWD'])


class ImmoSearchModel(Model):
    """Basic database model for immosearch"""

    class Meta:
        database = database
        schema = database.database


@create
class ImmoSearchUser(ImmoSearchModel):
    """User entry for immosearch control data"""

    customer = ForeignKeyField(Customer, db_column='customer',
                               related_name='immosearch')
    """The appropriate customer"""
    enabled = BooleanField(default=False)
    """Flag whether immosearch is enabled for the respective customer"""
    ignore_restrictions = BooleanField(default=False)
    """Flag whether immosearch should ignore
    real estate forwarding restrictions"""
    max_handlers = IntegerField(11, default=10)
    """Maximum amount of queries that can be performed at a time"""
    current_handlers = IntegerField(11)
    """Currently open handlers"""
    max_bytes = IntegerField(11, default=134217728)  # = 128 MiB
    """Maximum amount of bytes that can be handled for this user"""
    current_bytes = IntegerField(11)
    """Current amount of bytes opened for the customer"""
    protected = BooleanField(default=True)
    """Flag whether access to this resource is password protected"""
    auth_token = CharField(36, null=True)
    """A UUID-4 style authentication string"""
