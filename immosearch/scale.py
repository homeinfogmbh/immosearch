"""Image scaling"""

from PIL import Image
from tempfile import NamedTemporaryFile
from base64 import b64encode

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '26.02.2015'
__all__ = ['ImageScaler']


class ImageScaler():
    """HTML image file wrapping"""

    def __init__(self, file, scaling=None):
        """Initializes with file"""
        self._file = file
        self._scaling = scaling

    @property
    def file(self):
        """Returns the file's path"""
        return self._file

    @property
    def scaling(self):
        """Returns the scaling"""
        return self._scaling

    @property
    def data(self):
        """Returns the (scaled) image's data"""
        if self._scaling is None:
            with open(self.file, 'rb') as f:
                data = f.read()
        else:
            img = Image.open(self.file)
            img = img.resize(self._scaling, Image.ANTIALIAS)
            with NamedTemporaryFile('wb') as tmp:
                img.save(tmp.name, img.format)
                with open(tmp.name) as src:
                    data = src.read()
        return data

    @property
    def b64data(self):
        """Returns the file's data base64-encoded"""
        return b64encode(self.data)
