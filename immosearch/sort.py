"""Real estate sorting"""

from .lib import RealEstate
from .errors import InvalidSortingOption

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['RealEstateSorter']


class Key():
    """An attribute, that can be sorted"""

    def __init__(self, val):
        """Sets the actual value"""
        self._val = val

    @property
    def val(self):
        """Returns the value"""
        return self._val

    def __eq__(self, other):
        """Equality check"""
        return self.val == other.val

    def __gt__(self, other):
        """Greater-than check"""
        if self.val is None:
            return False
        elif other.val is None:
            return True
        else:
            return self.val > other.val

    def __lt__(self, other):
        """Less-than check"""
        if self.val is None:
            return True
        elif other.val is None:
            return False
        else:
            return self.val < other.val

    def __ge__(self, other):
        """Greater-or-equal check"""
        return (self.val == other.val) or self.__gt__(other)

    def __le__(self, other):
        """Less-or-equal check"""
        return (self.val == other.val) or self.__lt__(other)


class Sorting():
    """Sorting types"""

    ASC = True
    DESC = False


class RealEstateSorter():
    """Class that sorts real estates
    of a realtor by certain attributes
    """

    options = {'objektart': lambda f: f.objektart,
               'objekttyp': lambda f: f.objekttypen,
               'land': lambda f: f.land,
               'ort': lambda f: f.ort,
               'ortsteil': lambda f: f.ortsteil,
               'plz': lambda f: f.plz,
               'strasse': lambda f: f.strasse,
               'hausnummer': lambda f: f.hausnummer,
               'zimmer': lambda f: f.zimmer,
               'etage': lambda f: f.etage,
               'etagen': lambda f: f.etagen,
               'wohnflaeche': lambda f: f.wohnflaeche,
               'grundstuecksflaeche': lambda f: f.grundstuecksflaeche,
               'balkone': lambda f: f.balkone,
               'terrassen': lambda f: f.terrassen,
               'kaltmiete': lambda f: f.kaltmiete,
               'warmmiete': lambda f: f.warmmiete,
               'nebenkosten': lambda f: f.nebenkosten,
               'kaufpreis': lambda f: f.kaufpreis,
               'pacht': lambda f: f.pacht,
               'erbpacht': lambda f: f.erbpacht,
               'aussen_courtage': lambda f: f.aussen_courtage,
               'innen_courtage': lambda f: f.innen_courtage,
               'openimmo_obid': (str, lambda f: f.openimmo_obid),
               'objektnr_intern': (str, lambda f: f.objektnr_intern),
               'objektnr_extern': (str, lambda f: f.objektnr_extern),
               'barrierefrei': lambda f: f.barrierefrei,
               'haustiere': lambda f: f.haustiere,
               'raucher': lambda f: f.raucher,
               'kaufbar': lambda f: f.kaufbar,
               'mietbar': lambda f: f.mietbar,
               'erbpachtbar': lambda f: f.erbpachtbar,
               'leasing': lambda f: f.leasing,
               'abdatum': lambda f: f.abdatum,
               'moebliert': lambda f: f.moebliert,
               'seniorengerecht': lambda f: f.seniorengerecht,
               'baujahr': (str, lambda f: f.baujahr),
               'epart': lambda f: f.epart,
               'energieverbrauchkennwert':
                   lambda f: f.energieverbrauchkennwert,
               'endenergiebedarf': lambda f: f.endenergiebedarf,
               'primaerenergietraeger': lambda f: f.primaerenergietraeger,
               'stromwert': lambda f: f.stromwert,
               'waermewert': lambda f: f.waermewert,
               'wertklasse': lambda f: f.wertklasse,
               'min_mietdauer': lambda f: f.min_mietdauer,
               'max_mietdauer': lambda f: f.max_mietdauer,
               'laufzeit': lambda f: f.laufzeit,
               'max_personen': lambda f: f.max_personen}

    def __init__(self, immobilie, sort_options):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>)
        """
        self._immobilie = immobilie
        self._sort_options = sort_options

    @property
    def immobilie(self):
        """Returns the real estates"""
        return self._immobilie

    @property
    def sort_options(self):
        """Returns the sorting options"""
        return self._sort_options

    def _sort(self, real_estates, sort_option):
        """Sorts by exactly one sorting option"""
        option, desc = sort_option
        option_func = self.options.get(option)
        if option_func is None:
            raise InvalidSortingOption(option)
        else:
            result = sorted(real_estates, key=lambda r: Key(option_func(r)))
            if desc:
                result = reversed(result)
            return result

    def sort(self):
        """Sieve real estates by the given filters"""
        real_estates = (RealEstate(r) for r in self.immobilie)
        for sort_option in self.sort_options:
            real_estates = self._sort(real_estates, sort_option)
        for real_estate in real_estates:
            yield real_estate.immobilie
