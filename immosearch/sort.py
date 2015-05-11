"""Real estate sorting"""

from operator import itemgetter
from .lib import RealEstateWrapper
from .errors import InvalidSortingOption

__all__ = ['Sortable']


class Key():
    """A key, that can be sorted"""

    def __init__(self, val, desc=False):
        """Sets the actual value"""
        self._val = val
        self._desc = desc

    @property
    def val(self):
        """Returns the value"""
        return self._val

    @property
    def desc(self):
        """Determines whether we are in descending mode"""
        return self._desc

    def __eq__(self, other):
        """Equality check"""
        return self.val == other.val

    def _gt(self, other):
        """Greater-than check"""
        if self.val is None:
            return False
        elif other.val is None:
            return True
        else:
            return self.val > other.val

    def _lt(self, other):
        """Less-than check"""
        if self.val is None:
            return True
        elif other.val is None:
            return False
        else:
            return self.val < other.val

    def __gt__(self, other):
        """Greater-than check"""
        return not self._gt(other) if self.desc else self._gt(other)

    def __lt__(self, other):
        """Less-than check"""
        return not self._lt(other) if self.desc else self._lt(other)

    def __ge__(self, other):
        """Greater-or-equal check"""
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other):
        """Less-or-equal check"""
        return self.__eq__(other) or self.__lt__(other)


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

    @property
    def _keyed(self):
        """Generates (<keys>, <real_estate>) tuples"""
        for real_estate in (RealEstateWrapper(r) for r in self.immobilie):
            keys = []
            for sort_option in self.sort_options:
                option, desc = sort_option
                option_func = self.options.get(option)
                if option_func is None:
                    raise InvalidSortingOption(option)
                else:
                    keys.append(Key(option_func(real_estate), desc=desc))
            yield (keys, real_estate)

    def __iter__(self):
        """Sort real estates by the given options"""
        for _, real_estate in sorted(self._keyed, key=itemgetter(0)):
            yield real_estate.immobilie
