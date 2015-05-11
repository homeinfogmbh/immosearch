"""Abstract base classes for real estate and attachment iteration"""

__all__ = ['RealEstateIterator', 'AttachmentIterator']


class RealEstateIterator():
    """Class that iterates over its real estates"""

    def __init__(self, real_estates):
        """Sets the real estates to iterate over"""
        self._real_estates = real_estates

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    def __iter__(self):
        """Yields filtered / selected or sorted real estates"""
        raise NotImplementedError()


class AttachmentIterator():
    """Class that iterates over attachments"""

    def __init__(self, attachments):
        """Sets the real estates to iterate over"""
        self._attachments = attachments

    @property
    def attachments(self):
        """Returns the attachments"""
        return self._attachments

    def __iter__(self):
        """Yields filtered / selected or sorted real estates"""
        raise NotImplementedError()
