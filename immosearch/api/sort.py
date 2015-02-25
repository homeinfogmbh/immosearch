"""Real estate sorting"""

# TODO: Sort options:
# from .lib import Sorting

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['Sortable']


# TODO: sort parameters:
"""
PLZ
Hausnummer

Zimmer
Etage
Wohnfläche
Grundstücksfläche

Kaltmiete
Warmmiete
Nebenkosten
Kaufpreis
"""


class Sortable():
    """An OpenImmo™ immobilie wrapper, that can be sorted"""

    def __init__(self, immobilie, keys=None):
        """Creates a new instance"""
        self._immobilie = immobilie
        self.keys = [] if keys is None else keys

    @property
    def immobilie(self):
        """Returns the OpenImmo™ immobilie"""
        return self._immobilie

    def __eq__(self, other):
        """Equality comparison"""
        return self.keys == other.keys

    def __gt__(self, other):
        """Greater-than comparison"""
        return self.keys > other.keys

    def __lt__(self, other):
        """Less-than comparison"""
        return self.keys < other.keys

    def __ge__(self, other):
        """Greater-than or equal comparison"""
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other):
        """Less-than or equal comparison"""
        return self.__eq__(other) or self.__lt__(other)
