"""Image scaling"""

from tempfile import NamedTemporaryFile
from base64 import b64encode
from PIL import Image

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '26.02.2015'
__all__ = ['ScaledImage']


class ScaledImage():
    """A scaled image wrapper"""

    def __init__(self, file, resolution=None):
        """Initializes with file and optional resolution
        XXX: resolution must be a tuple: (<width>, <height>)
        """
        self._file = file
        self.resolution = resolution

    @property
    def file(self):
        """Returns the file's path"""
        return self._file

    @property
    def data(self):
        """Returns the (scaled) image's data"""
        if self.resolution is None:
            with open(self.file, 'rb') as f:
                data = f.read()
        else:
            img = Image.open(self.file)
            scaled_img = img.resize(self.resolution, Image.ANTIALIAS)
            with NamedTemporaryFile('wb') as tmp:
                scaled_img.save(tmp.name, img.format)
                with open(tmp.name, 'rb') as src:
                    data = src.read()
        return data

    @property
    def size(self):
        """Returns the file's size"""
        return len(self.data)

    @property
    def b64data(self):
        """Returns the file's data base64-encoded"""
        return b64encode(self.data)

    @property
    def b64size(self):
        """Returns the file's size"""
        return len(self.b64data)
