"""Realtor and real estate filtering"""

from peewee import MySQLDatabase, Model, IntegerField, BooleanField,\
    ForeignKeyField, CharField, create

from homeinfo.crm import Customer

from .config import db

__all__ = ['ImmoSearchUser']

database = MySQLDatabase(
    db['DB'], host=db['HOST'],
    user=db['USER'], passwd=db['PASSWD'])


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
    enabled = BooleanField(default=False)
    ignore_restrictions = BooleanField(default=False)
    max_handlers = IntegerField(11, default=10)
    _current_handlers = IntegerField(11, db_column='current_handlers')
    max_bytes = IntegerField(11, default=134217728)  # = 128 MiB
    protected = BooleanField(default=True)
    auth_token = CharField(36, null=True)

    @property
    def cid(self):
        """Returns the customer ID"""
        return self.customer.id

    @property
    def name(self):
        """Returns the customer's name"""
        return self.customer.name

    @property
    def current_handlers(self):
        """Returns the current handlers"""
        return self._current_handlers

    @current_handlers.setter
    def current_handlers(self, current_handlers):
        """Sets the currently open handlers and saves the record"""
        if current_handlers >= 0:
            self._current_handlers = current_handlers
        else:
            self._current_handlers = 0
        self.save()
