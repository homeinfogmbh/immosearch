"""Real estate data selecting"""

__all__ = ['Selections', 'RealEstateDataSelector']


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


class RealEstateDataSelector():
    """Class that filters real estates of a user"""

    def __init__(self, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        self._real_estates = real_estates
        self._selections = selections or []

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

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
