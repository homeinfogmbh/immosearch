"""Attachment filtering and manipulation"""

from contextlib import suppress
from openimmo import openimmo
from openimmo.openimmo import AttachmentError
from .abc import AttachmentIterator
from .errors import InvalidLimiting

__all__ = ['Selections', 'RealEstateSelector']

# Available picture types
PIC_TYPES = ['image/jpeg', 'image/png', 'image/gif']


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


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

    def __init__(self, attachments, attachment_limit=None, picture_limit=None,
                 floorplan_limit=None, document_limit=None):
        """Initializes with a with attachments and limiting options"""
        super().__init__(attachments)
        self._attachment_limit = attachment_limit   # Global attachment limit
        self._picture_limit = picture_limit
        self._floorplan_limit = floorplan_limit
        self._document_limit = document_limit
        try:
            self._chklimits()
        except ValueError as ve:
            raise InvalidLimiting(str(ve))

    @property
    def _limit_sum(self):
        """Sums up the specific limits"""
        limit_sum = 0
        if self.picture_limit is not None:
            if self.picture_limit >= 0:
                limit_sum += self.picture_limit
            else:
                raise ValueError('Limit must be greater or equal zero')
        if self.floorplan_limit is not None:
            if self.floorplan_limit >= 0:
                limit_sum += self.floorplan_limit
            else:
                raise ValueError('Limit must be greater or equal zero')
        if self.document_limit is not None:
            if self.document_limit >= 0:
                limit_sum += self.document_limit
            else:
                raise ValueError('Limit must be greater or equal zero')
        return limit_sum

    def _chklimits(self):
        """Checks limits for sanity"""
        limit_sum = self._limit_sum
        if limit_sum:
            if self.attachment_limit:
                if limit_sum > self.attachment_limit:
                    raise ValueError('Sum of specific must not exceed'
                                     ' general attachment limit')
                else:
                    return True
            else:
                return True
        else:
            if self.attachment_limit:
                return True
            else:
                raise ValueError('Must specify either a general'
                                 ' limit or specific limits')

    @property
    def attachment_limit(self):
        """Returns the attachment limit"""
        return self._attachment_limit

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

    def __iter__(self):
        """Yields limited attachments"""
        picture_cnt = 0
        floorplan_cnt = 0
        document_cnt = 0
        for cnt, attachment in enumerate(self.attachments):
            # Break loop if global limit has been exceeded
            if self.attachment_limit is not None:
                if cnt > self.attachment_limit:
                    break
            # Limit pictures, but exclude floor plans,
            # since we limit them separately below
            if (attachment.gruppe != 'GRUNDRISS' and
                    attachment.gruppe in openimmo.BILDER):
                if self.picture_limit is not None:
                    if picture_cnt < self.picture_limit:
                        picture_cnt += 1
                        yield attachment
                else:
                    yield attachment
            elif attachment.gruppe == 'GRUNDRISS':
                if self.floorplan_limit is not None:
                    if floorplan_cnt < self.floorplan_limit:
                        floorplan_cnt += 1
                        yield attachment
                else:
                    yield attachment
            elif attachment.gruppe == 'DOKUMENTE':
                if self.document_limit is not None:
                    if document_cnt < self.document_limit:
                        document_cnt += 1
                        yield attachment
                else:
                    yield attachment
            # Yield all other attachments as long as  the
            # global limit has not yet been exceeded
            else:
                yield attachment


class AttachmentLoader(AttachmentIterator):
    """Loads attachment data that is not remote into base64 data"""

    def __iter__(self):
        """Performs the loading"""
        for attachment in self.attachments:
            with suppress(AttachmentError):
                yield attachment.insource()
