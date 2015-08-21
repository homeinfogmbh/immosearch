"""Image scaling"""

from tempfile import NamedTemporaryFile

from PIL import Image

from .errors import NoScalingProvided

__all__ = ['ImageScaler']


def scale_aspect_ratio(original, new, maximum=False):
    """Scales an image, keeping its aspect ratio"""
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


class ScaledImage():
    """A scaled image wrapper"""

    def __init__(self, file, resolution):
        """Initializes with file and optional resolution
        XXX: resolution must be a tuple: (<width>, <height>)
        """
        self._file = file
        self._resolution = resolution

    @property
    def file(self):
        """Returns the file's path"""
        return self._file

    @property
    def resolution(self):
        """Returns the resolution"""
        return self._resolution

    @property
    def width(self):
        """Returns the target width"""
        return self.resolution[0]

    @property
    def height(self):
        """Returns the target height"""
        return self.resolution[1]

    @property
    def data(self):
        """Returns the (scaled) image's data"""
        img = Image.open(self.file)
        width, height = img.size
        # Only scale bigger images
        if width > self.width or height > self.height:
            target_resolution = scale_aspect_ratio(
                (width, height), self.resolution)
            scaled_img = img.resize(target_resolution, Image.ANTIALIAS)
            with NamedTemporaryFile('wb') as tmp:
                scaled_img.save(tmp.name, img.format)
                with open(tmp.name, 'rb') as src:
                    return src.read()
        else:
            with open(self.file, 'rb') as f:
                return f.read()


class ImageScaler():
    """Class that scales an attachment"""

    def __init__(self, resolution):
        """Class to scale attachments of real estates"""
        self._resolution = resolution

    @property
    def resolution(self):
        """Returns the targeted resolution"""
        return self._resolution

    def scale(self, image):
        """Returns the real estates with scaled attachments
        XXX: Image is assumed to be external or internal - NOT remote
        """
        if self.resolution is None:
            raise NoScalingProvided()
        with NamedTemporaryFile('wb') as tmp:
            tmp.write(image.data)
            scaled = ScaledImage(tmp.name, self.resolution)
            try:
                image.data = scaled.data
            except OSError:
                return image.insource()
            else:
                return image
