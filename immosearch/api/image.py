"""
Image encoding
"""
from homeinfo.util import MIMEUtil
from base64 import b64encode

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['Image']


class Image():
    """
    Encodes attachments
    """
    def __init__(self, file):
        """Initializes with file"""
        self.__file = file

    @property
    def data(self):
        """Returns the file's data"""
        with open(self.__file, 'rb') as f:
            return f.read()

    @property
    def mimetype(self):
        """returns the file's MIME-Type"""
        return MIMEUtil.getmime(self.__file)

    @property
    def b64data(self):
        """Returns the base64-encoded data of the file"""
        return b64encode(self.data)

    @property
    def _b64str(self):
        """Returns a base64-style string without the trailing '='"""
        return str(self.b64data).replace('\'', '').replace('=', '')

    def tohtml(self):
        """Returns the file converted for HTML embedding"""
        return '"'.join(['<img src=',
                         ';'.join([':'.join(['data', self.mime]),
                                   ','.join(['base64', self._b64str])]),
                         '">'])
