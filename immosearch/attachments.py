"""Attachment filtering and manipulation"""

from openimmo import openimmo
from openimmo.openimmo import AttachmentError

from .imgscale import ImageScaler

__all__ = ['AttachmentSelector', 'AttachmentLimiter', 'AttachmentLoader']


class AttachmentWrapper():
    """Class that wraps attachments"""

    def __init__(self, attachments):
        """Sets the real estates to iterate over"""
        self._attachments = attachments

    @property
    def attachments(self):
        """Returns the attachments"""
        return self._attachments


class AttachmentSelector(AttachmentWrapper):
    """Class that filters real estates of a user"""

    def __init__(self, attachments, indexes=None, titles=None, groups=None):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        super().__init__(attachments)
        self._indexes = indexes
        self._titles = titles
        self._groups = groups

    @property
    def indexes(self):
        """Returns the attachment indexes"""
        return self._indexes

    @property
    def titles(self):
        """Returns the attachment title"""
        return self._titles

    @property
    def groups(self):
        """Returns the attachment group"""
        return self._groups

    def __iter__(self):
        """Yields selected attachments"""
        if (self.indexes is None and
                self.titles is None and
                self.groups is None):
            yield from self.attachments
        else:
            for cnt, attachment in enumerate(self.attachments):
                if self.indexes is not None:
                    if cnt in self.indexes:
                        yield attachment
                        continue
                if self.titles is not None:
                    if attachment.anhangtitel in self.titles:
                        yield attachment
                        continue
                if self.groups is not None:
                    if attachment.gruppe in self.groups:
                        yield attachment
                        continue


class AttachmentLimiter(AttachmentWrapper):
    """Class that filters real estates of a user"""

    def __init__(self, attachments, picture_limit=None,
                 floorplan_limit=None, document_limit=None):
        """Initializes with a with attachments and limiting options"""
        super().__init__(attachments)
        self._picture_limit = picture_limit
        self._floorplan_limit = floorplan_limit
        self._document_limit = document_limit

    def picture_limit(self, offset=None):
        """Returns the picture limit"""
        if offset:
            limit = self._picture_limit - offset
        else:
            limit = self._picture_limit or 0
        return limit if limit > 0 else 0

    def floorplan_limit(self, offset=None):
        """Returns the floor plan limit"""
        if offset:
            limit = self._floorplan_limit - offset
        else:
            limit = self._floorplan_limit or 0
        return limit if limit > 0 else 0

    def document_limit(self, offset=None):
        """Returns the document limit"""
        if offset:
            limit = self._document_limit - offset
        else:
            limit = self._document_limit or 0
        return limit if limit > 0 else 0

    @property
    def whitelist(self):
        """Yields white-listed attachments,
        which are yielded in any case
        """
        for attachment in self.attachments:
            if attachment.remote:
                yield attachment

    @property
    def greylist(self):
        """Yields attachments that are subject to limitations"""
        for attachment in self.attachments:
            if attachment.external or attachment.internal:
                yield attachment

    @property
    def pictures(self):
        """Yields pictures, but no floor plans"""
        for attachment in self.greylist:
            if attachment.gruppe in openimmo.BILDER:
                if attachment.gruppe != 'GRUNDRISS':
                    yield attachment

    @property
    def floorplans(self):
        """Yields floor plans"""
        for attachment in self.greylist:
            if attachment.gruppe == 'GRUNDRISS':
                yield attachment

    @property
    def documents(self):
        """Yields documents"""
        for attachment in self.greylist:
            if attachment.gruppe == 'DOKUMENTE':
                yield attachment

    def __iter__(self):
        """Yields limited attachments"""
        pictures = 0
        floorplans = 0
        documents = 0
        for attachment in self.whitelist:
            if attachment.gruppe in openimmo.BILDER:
                if attachment.gruppe != 'GRUNDRISS':
                    pictures += 1
                else:
                    floorplans += 1
            elif attachment.gruppe == 'DOKUMENTE':
                documents += 1
            yield attachment
        for index, picture in enumerate(self.pictures):
            if index < self.picture_limit(pictures):
                yield picture
            else:
                break
        for index, floorplan in enumerate(self.floorplans):
            if index < self.floorplan_limit(floorplans):
                yield floorplan
            else:
                break
        for index, document in enumerate(self.documents):
            if index < self.document_limit(documents):
                yield document
            else:
                break


class AttachmentLoader(AttachmentWrapper):
    """Loads attachment data that is not remote into base64 data"""

    def __init__(self, attachments, byte_limit, scaling):
        """Sets attachments and image scaler"""
        super().__init__(attachments)
        self._byte_limit = byte_limit
        self._img_scaler = ImageScaler(scaling)

    @property
    def byte_limit(self):
        """Returns the byte limit"""
        return self._byte_limit or 0

    @property
    def img_scaler(self):
        """Returns the image scaler"""
        return self._img_scaler

    def __iter__(self):
        """Loads external attachments"""
        used_bytes = 0
        for attachment in self.attachments:
            if attachment.remote:
                yield attachment
            else:
                if attachment.gruppe in openimmo.BILDER:
                    internal_picture = self._img_scaler.scale(attachment)
                    used_bytes += len(internal_picture.data)
                    if used_bytes <= self.byte_limit:
                        yield internal_picture
                else:
                    try:
                        internal_data = attachment.insource()
                    except AttachmentError:
                        continue
                    else:
                        used_bytes += len(internal_data.data)
                        if used_bytes <= self.byte_limit:
                            yield internal_data
