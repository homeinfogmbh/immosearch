"""HTML data wrapping"""

from homeinfolib import mimetype
from base64 import b64encode
from openimmo import openimmo
from .lib import tags, Delims

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['Image', 'RealEstate']


# XXX: This is obsolete, since rendering
# is being performed by Niko's front-end


class Image():
    """HTML image file wrapping"""

    def __init__(self, file):
        """Initializes with file"""
        self._file = file

    @property
    def data(self):
        """Returns the file's data"""
        with open(self._file, 'rb') as f:
            return f.read()

    @property
    def mimetype(self):
        """returns the file's MIME-Type"""
        return mimetype(self._file)

    @property
    def b64data(self):
        """Returns the base64-encoded data of the file"""
        return b64encode(self.data)

    @property
    def b64html(self):
        """Returns a base64-style HTML compliant string
        without:
            - the "'" high comma delimiters
            - the trailing '='
        """
        return str(self.b64data).replace('\'', '').replace('=', '')

    @property
    def html(self):
        """Returns the file converted for HTML embedding"""
        return '"'.join(['<img src=',
                         ';'.join([':'.join(['data', self.mimetype]),
                                   ','.join(['base64', self.b64html])]),
                         '>'])


class RealEstate():
    """A wrapper that renders an OpenImmo™-<immobile>-style
    real estate data into an HTML template
    """

    def __init__(self, immobilie, template, tag_open='<immobilie ',
                 tag_close='/>'):
        """Sets immobilie, template and tags"""
        if type(immobilie) == str:
            self._immobilie = openimmo.CreateFromDocument(immobilie)
        else:
            self._immobilie = immobilie
        try:
            with open(template, 'r') as f:
                self._template = f.read()
        except FileNotFoundError:
            self._template = template
        self._tag_open = tag_open
        self._tag_close = tag_close

    @property
    def _tags(self):
        """Yields tags found in the template"""
        return tags(self._template, tag_open=self._tag_open,
                    tag_close=self._tag_close)

    def _getval(self, field):
        """Returns the value of a desired field"""
        elem = self._immobilie
        for node in field.split('.'):
            index = None
            if node.endswith(Delims.END_INDEX):
                for tag in tags(node, tag_open=Delims.BEGIN_INDEX,
                                tag_close=Delims.END_INDEX):
                    try:
                        index = int(tag)
                    except (ValueError, TypeError):
                        continue
                    else:
                        break
            try:
                elem = getattr(elem, node)
            except AttributeError:
                elem = None
                break
            else:
                if index is not None:
                    try:
                        elem = elem[index]
                    except (IndexError, TypeError):
                        elem = None
                        break
        return elem

    @property
    def _dict(self):
        """Returns the translation dictionary"""
        result = {}
        for k in self._tags:
            v = self._getval(k)
            result[self._tag_open + k + self._tag_close] = v
        return result

    def render(self):
        """Render the real estate into the HTML template"""
        result = self._template
        d = self._dict
        for k in d:
            result = result.replace(k, d[k])
        return result
