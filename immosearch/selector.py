"""Real estate data selecting"""

from .abc import RealEstateIterator

__all__ = ['Selections', 'RealEstateDataSelector']


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


class RealEstateDataSelector(RealEstateIterator):
    """Class that filters real estates of a user"""

    def __init__(self, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        super().__init__(real_estates)
        self._selections = selections or []

    @property
    def selections(self):
        """Returns the selections"""
        return self._selections

    def __iter__(self):
        """Returns real estates liited to the selections"""
        for real_estate in self.real_estates:
            # Discard freitexte iff not selected
            if Selections.FREITEXTE not in self.selections:
                real_estate.freitexte = None
            # Discard attachments iff not selected
            if Selections.ATATCHMENTS not in self.selections:
                real_estate.anhaenge = None
            yield real_estate
