"""QR code generation"""

from pyqrcode import QRCode
from PIL import Image
from tempfile import NamedTemporaryFile

__all__ = ['PNGQRCode']


class PNGQRCode():
    """An PNG formatted QR code generator"""

    def __init__(self, base_url, idents=None, scale=None):
        """Sets the base URL"""
        self._base_url = base_url
        self._idents = idents
        self._scale = scale or 5

    def _mkqrcode(self):
        """Generates the actual QR code"""
        if self._idents is not None:
            url = self._base_url.format(*self._idents)
        else:
            url = self._base_url
        qrcode = QRCode(url)
        with NamedTemporaryFile('rb', suffix='.png') as tmp:
            qrcode.png(tmp.name, self._scale)
            tmp.seek(0)
            qr_data = tmp.read()
        return qr_data

    def _insert_logo(self, qr_data, logo_data):
        """Inserts a logo into a QR code image"""
        with NamedTemporaryFile('w+b', suffix='.png') as qr_tmp:
            qr_tmp.write(qr_data)
            qr_tmp.seek(0)
            qr_image = Image.open(qr_tmp.name, 'r')
        qr_image = qr_image.convert('RGB')  # Convert greyscale to RGB
        qr_w, qr_h = qr_image.size
        with NamedTemporaryFile('w+b', suffix='.png') as logo_tmp:
            logo_tmp.write(logo_data)
            logo_tmp.seek(0)
            logo_image = Image.open(logo_tmp.name, 'r')
        logo_w, logo_h = logo_image.size
        offset = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
        # Insert logo on foreground with transparency
        qr_image.paste(logo_image, offset, logo_image)
        # Show background through transparency of logo
        qr_image.show()
        with NamedTemporaryFile('w+b', suffix='.png') as qr_tmp:
            qr_image.save(qr_tmp.name)
            qr_tmp.seek(0)
            qr_data = qr_tmp.read()
        return qr_data

    def render(self, logo=None):
        """Renders a QR-code"""
        qr_data = self._mkqrcode()
        if logo is not None:
            qr_data = self._insert_logo(qr_data, logo)
        return qr_data
