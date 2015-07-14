"""Attachment filtering and manipulation"""

from contextlib import suppress

from openimmo import openimmo
from openimmo.openimmo import AttachmentError

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

    def __init__(self, attachments, byte_limit=None, picture_limit=None,
                 floorplan_limit=None, document_limit=None):
        """Initializes with a with attachments and limiting options"""
        super().__init__(attachments)
        self._byte_limit = byte_limit
        self._picture_limit = picture_limit
        self._floorplan_limit = floorplan_limit
        self._document_limit = document_limit

    def picture_limit(self, offset=None):
        """Returns the picture limit"""
        if offset:
            limit = self._picture_limit - offset
        else:
            limit = self._picture_limit
        return limit if limit > 0 else 0

    def floorplan_limit(self, offset=None):
        """Returns the floor plan limit"""
        if offset:
            limit = self._floorplan_limit - offset
        else:
            limit = self._floorplan_limit
        return limit if limit > 0 else 0

    def document_limit(self, offset=None):
        """Returns the document limit"""
        if offset:
            limit = self._document_limit - offset
        else:
            limit = self._document_limit
        return limit if limit > 0 else 0

    @property
    def byte_limit(self):
        """Returns the byte limit"""
        return self._byte_limit or 0

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
        used_bytes = 0
        for index, picture in enumerate(self.pictures):
            used_bytes += len(picture.data)
            if (used_bytes <= self.byte_limit and
                    index < self.picture_limit(pictures)):
                yield picture
            else:
                break
        for index, floorplan in enumerate(self.floorplans):
            used_bytes += len(floorplan.data)
            if (used_bytes <= self.byte_limit and
                    index < self.floorplan_limit(floorplans)):
                yield floorplan
            else:
                break
        for index, document in enumerate(self.documents):
            used_bytes += len(document.data)
            if (used_bytes <= self.byte_limit and
                    index < self.document_limit(documents)):
                yield document
            else:
                break


class AttachmentLoader(AttachmentWrapper):
    """Loads attachment data that is not remote into base64 data"""

    def __iter__(self):
        """Loads external attachments"""
        for attachment in self.attachments:
            with suppress(AttachmentError):
                yield attachment.insource()
