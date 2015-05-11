"""Image scaling"""

from contextlib import suppress
from tempfile import NamedTemporaryFile
from base64 import b64encode
from PIL import Image
from .errors import NoScalingProvided

__all__ = ['AttachmentScaler']


def keep_aspect_ratio(original, new, maximum=False):
    """Gets the minimal or maximal factor for image scaling"""
    ox, oy = original
    nx, ny = new
    delta_x = nx / ox
    delta_y = ny / oy
    if delta_x > delta_y:
        if maximum:
            return (nx, round(oy*delta_x))
        else:
            return (round(ox*delta_y), ny)
    elif delta_x < delta_y:
        if maximum:
            return (round(ox*delta_y), ny)
        else:
            return (nx, round(oy*delta_x))
    else:
        return (nx, ny)


class AttachmentScaler():
    """Class that scales an attachment"""

    def __init__(self, immobilie, resolution):
        """Class to scale attachments of real estates"""
        self._immobilie = immobilie
        self._resolution = resolution

    @property
    def immobilie(self):
        """Returns the real estates"""
        return self._immobilie

    @property
    def resolution(self):
        """Returns the targeted resolution"""
        return self._resolution

    def __iter__(self):
        """Returns the real estates with scaled attachments"""
        for immobilie in self.immobilie:
            if immobilie.anhaenge:
                processed = []
                for a in immobilie.anhaenge.anhang:
                    if a.external:
                        if self.resolution is None:
                            raise NoScalingProvided()
                        else:
                            with NamedTemporaryFile('wb') as tmp:
                                tmp.write(a.data)
                                with suppress(OSError):
                                    original_size = Image.open(tmp.name).size
                                    scaled = ScaledImage(
                                        tmp.name, keep_aspect_ratio(
                                            original_size, self.resolution))
                                    a.data = scaled.data
                                    processed.append(a)
                    else:
                        processed.append(a)
                immobilie.anhaenge.anhang = processed
            yield immobilie


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
