"""Attachment filtering and manipulation"""

from contextlib import suppress
from openimmo import openimmo
from openimmo.openimmo import AttachmentError
from .abc import AttachmentIterator
from .errors import InvalidLimiting

__all__ = ['AttachmentSelector']


class AttachmentSelector(AttachmentIterator):
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


class AttachmentLimiter(AttachmentIterator):
    """Class that filters real estates of a user"""

    def __init__(self, attachments, picture_limit=None,
                 floorplan_limit=None, document_limit=None):
        """Initializes with a with attachments and limiting options"""
        super().__init__(attachments)
        self._picture_limit = picture_limit
        self._floorplan_limit = floorplan_limit
        self._document_limit = document_limit

    @property
    def picture_limit(self):
        """Returns the picture limit"""
        return self._picture_limit

    @property
    def floorplan_limit(self):
        """Returns the floor plan limit"""
        return self._floorplan_limit

    @property
    def document_limit(self):
        """Returns the document limit"""
        return self._document_limit

    @property
    def pictures(self):
        """Yields pictures, but no floor plans"""
        for attachment in self.attachments:
            if (attachment.gruppe in openimmo.BILDER and
                    attachment.gruppe != 'GRUNDRISS'):
                yield attachment

    @property
    def floorplans(self):
        """Yields floor plans"""
        for attachment in self.attachments:
            if attachment.gruppe == 'GRUNDRISS':
                yield attachment

    @property
    def documents(self):
        """Yields documents"""
        for attachment in self.attachments:
            if attachment.external and attachment.gruppe == 'DOKUMENTE':
                yield attachment

    @property
    def whitelist(self):
        """Yields white-listed attachments,
        which are yielded in any case
        """
        for attachment in self.attachments:
            if attachment.remote and attachment.gruppe == 'DOKUMENTE':
                attachment.IMMOSEARCH_WHITELIST = True
                yield attachment

    def __iter__(self):
        """Yields limited attachments"""
        yield from self.whitelist
        if self.picture_limit is not None:
            for index, picture in enumerate(self.pictures):
                if index < self.picture_limit:
                    yield picture
                else:
                    break
        if self.floorplan_limit is not None:
            for index, floorplan in enumerate(self.floorplans):
                if index < self.floorplan_limit:
                    yield floorplan
                else:
                    break
        if self.document_limit is not None:
            for index, document in enumerate(self.documents):
                if index < self.document_limit:
                    yield document
                else:
                    break


class AttachmentLoader(AttachmentIterator):
    """Loads attachment data that is not remote into base64 data"""

    def __iter__(self):
        """Performs the loading"""
        for attachment in self.attachments:
            # Do not insource remote documents
            if attachment.remote and attachment.gruppe == 'DOKUMENTE':
                yield attachment
            else:
                with suppress(AttachmentError):
                    yield attachment.insource()
