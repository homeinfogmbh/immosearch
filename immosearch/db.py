"""Realtor and real estate filtering"""

from peewee import MySQLDatabase, Model, IntegerField, BooleanField,\
    ForeignKeyField, CharField, create

from homeinfo.crm import Customer

from .config import db

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
    _current_handlers = IntegerField(11, db_column='current_handlers')
    """Currently open handlers"""
    max_bytes = IntegerField(11, default=134217728)  # = 128 MiB
    """Maximum amount of bytes that can be handled for this user"""
    _current_bytes = IntegerField(11, db_column='current_bytes')
    """Current amount of bytes opened for the customer"""
    protected = BooleanField(default=True)
    """Flag whether access to this resource is password protected"""
    auth_token = CharField(36, null=True)
    """A UUID-4 style authentication string"""

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

    @property
    def current_bytes(self):
        """Returns the current bytes"""
        return self._current_bytes

    @current_bytes.setter
    def current_bytes(self, current_bytes):
        """Sets the currently used bytes and saves the record"""
        if current_bytes >= 0:
            self.current_bytes = current_bytes
        else:
            self.current_bytes = 0
        self.save()
