"""Image scaling"""

from contextlib import suppress
from tempfile import NamedTemporaryFile
from base64 import b64encode
from PIL import Image

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '26.02.2015'
__all__ = ['AttachmentScaler']


class AttachmentScaler():
    """Class that scales an attachment"""

    def __init__(self, real_estates, resolution):
        """Class to scale attachments of real estates"""
        self._real_estates = real_estates
        self._resolution = resolution

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def resolution(self):
        """Returns the targeted resolution"""
        return self._resolution

    @property
    def immobilie(self):
        """Returns the real estates with scaled attachments"""
        for i in self.real_estates:
            if i.anhaenge:
                processed = []
                for a in i.anhaenge.anhang:
                    if a.external:
                        if self.resolution is None:
                            a.data = a.data  # Insource data
                        else:
                            with NamedTemporaryFile('wb') as tmp:
                                tmp.write(a.data)
                                scaled = ScaledImage(tmp.name, self.resolution)
                                with suppress(OSError):
                                    a.data = scaled.b64data
                                    processed.append(a)
                    else:
                        processed.append(a)
                i.anhaenge.anhang = processed
            yield i


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
