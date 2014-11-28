"""
Real estate sorting
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['SortableRealEstate']


# TODO: properties:
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


class SortableRealEstate():
    """
    Wrapper class for an OpenImmo™-Immobilie
    that can be filtered by certain attributes
    """
    def __init__(self, immobilie):
        """Sets the appropriate OpenImmo™-immobilie"""
        self.__immobilie = immobilie
        # TODO: implement
