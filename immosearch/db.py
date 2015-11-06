"""Realtor and real estate filtering"""

from peewee import Model, IntegerField, BooleanField, ForeignKeyField,\
    CharField, BlobField

from homeinfo.peewee import MySQLDatabase, create
from homeinfo.crm import Customer

from .config import db
from .qrcode import PNGQRCode

__all__ = ['ImmoSearchUser', 'QRCode']

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


@create
class ImmoSearchUser(ImmoSearchModel):
    """User entry for immosearch control data"""

    customer = ForeignKeyField(
        Customer, db_column='customer', related_name='immosearch')
    enabled = BooleanField(default=False)
    ignore_restrictions = BooleanField(default=False)
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

    def authenticate(self, token):
        """Authenticates the user with a specified token"""
        if self.protected:
            if self.auth_token:
                if self.auth_token == token:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True


@create
class QRCode(ImmoSearchModel):
    """QR code service settings"""

    customer = ForeignKeyField(
        Customer, db_column='customer', related_name='qrcodes')
    base_url = CharField(255, default='http://{0}.{1}.123xp.de/')
    scale = IntegerField(default=2)
    logo = BlobField(null=True, default=None)   # XXX: Must be a PNG file!

    def render(self, immobilie):
        """Renders QR code for an OpenImmo immmobilie DOM"""
        idents = (immobilie.openimmo_obid, self.customer.id)
        qrcode = PNGQRCode(self.base_url, idents=idents, scale=self.scale)
        return qrcode.render(logo=self.logo)
