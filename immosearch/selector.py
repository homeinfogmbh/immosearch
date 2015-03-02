"""Real estate data filtering"""

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['Selections', 'RealEstateSelector']


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


class RealEstateSelector():
    """Class that filters real estates of a user"""

    def __init__(self, real_estates, selections):
        """Initializes with a user record"""
        self._real_estates = real_estates
        self._selections = selections

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def selections(self):
        """Returns the selections"""
        return self._selections

    @property
    def immobilie(self):
        """Returns real estates limited to the selections"""
        for real_estate in self.real_estates:
            if Selections.FREITEXTE not in self.selections:
                real_estate.freitexte = None
            if Selections.ATATCHMENTS not in self.selections:
                real_estate.anhaenge = None
            yield real_estate
