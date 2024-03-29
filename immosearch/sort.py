"""Real estate sorting."""

from enum import Enum
from operator import itemgetter
from typing import Any

from immosearch.filter import FilterableRealEstate
from immosearch.errors import InvalidSortingOption


__all__ = ["Sorting", "RealEstateSorter"]


OPTIONS = {
    "objektart": lambda f: f.objektart,
    "objekttyp": lambda f: f.objekttypen,
    "land": lambda f: f.land,
    "ort": lambda f: f.ort,
    "ortsteil": lambda f: f.ortsteil,
    "plz": lambda f: f.plz,
    "strasse": lambda f: f.strasse,
    "hausnummer": lambda f: f.hausnummer,
    "zimmer": lambda f: f.zimmer,
    "etage": lambda f: f.etage,
    "etagen": lambda f: f.etagen,
    "wohnflaeche": lambda f: f.wohnflaeche,
    "grundstuecksflaeche": lambda f: f.grundstuecksflaeche,
    "balkone": lambda f: f.balkone,
    "terrassen": lambda f: f.terrassen,
    "kaltmiete": lambda f: f.kaltmiete or f.nettokaltmiete,
    "warmmiete": lambda f: f.warmmiete,
    "gesamtmiete": lambda f: f.gesamtmiete,
    "nebenkosten": lambda f: f.nebenkosten,
    "heizkosten": lambda f: f.heizkosten,
    "kaufpreis": lambda f: f.kaufpreis,
    "pacht": lambda f: f.pacht,
    "erbpacht": lambda f: f.erbpacht,
    "aussen_courtage": lambda f: f.aussen_courtage,
    "innen_courtage": lambda f: f.innen_courtage,
    "openimmo_obid": (str, lambda f: f.openimmo_obid),
    "objektnr_intern": (str, lambda f: f.objektnr_intern),
    "objektnr_extern": (str, lambda f: f.objektnr_extern),
    "barrierefrei": lambda f: f.barrierefrei,
    "haustiere": lambda f: f.haustiere,
    "raucher": lambda f: f.raucher,
    "kaufbar": lambda f: f.kaufbar,
    "mietbar": lambda f: f.mietbar,
    "erbpachtbar": lambda f: f.erbpachtbar,
    "leasing": lambda f: f.leasing,
    "abdatum": lambda f: f.abdatum,
    "moebliert": lambda f: f.moebliert,
    "seniorengerecht": lambda f: f.seniorengerecht,
    "baujahr": (str, lambda f: f.baujahr),
    "epart": lambda f: f.epart,
    "energieverbrauchkennwert": lambda f: f.energieverbrauchkennwert,
    "endenergiebedarf": lambda f: f.endenergiebedarf,
    "primaerenergietraeger": lambda f: f.primaerenergietraeger,
    "stromwert": lambda f: f.stromwert,
    "waermewert": lambda f: f.waermewert,
    "wertklasse": lambda f: f.wertklasse,
    "min_mietdauer": lambda f: f.min_mietdauer,
    "max_mietdauer": lambda f: f.max_mietdauer,
    "laufzeit": lambda f: f.laufzeit,
    "max_personen": lambda f: f.max_personen,
}


class Key:
    """A key, that can be sorted."""

    def __init__(self, val: Any, desc: bool = False):
        """Sets the actual value."""
        self.val = val
        self.desc = desc

    def __eq__(self, other: Any):
        """Equality check."""
        return self.val == other.val

    def _gt(self, other: Any) -> bool:
        """Greater-than check."""
        if self.val is None:
            return False

        if other.val is None:
            return True

        return self.val > other.val

    def _lt(self, other: Any) -> bool:
        """Less-than check."""
        if self.val is None:
            return True

        if other.val is None:
            return False

        return self.val < other.val

    def __gt__(self, other: Any):
        """Greater-than check."""
        return not self._gt(other) if self.desc else self._gt(other)

    def __lt__(self, other: Any):
        """Less-than check."""
        return not self._lt(other) if self.desc else self._lt(other)

    def __ge__(self, other: Any):
        """Greater-or-equal check."""
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other: Any):
        """Less-or-equal check."""
        return self.__eq__(other) or self.__lt__(other)


class Sorting(Enum):
    """Sorting types."""

    ASC = True
    DESC = False


class RealEstateSorter:
    """Class that sorts real estates
    of a realtor by certain attributes.
    """

    def __init__(self, real_estates, sort_options):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>).
        """
        self.real_estates = real_estates
        self.sort_options = sort_options or []

    def __iter__(self):
        """Sort real estates by the given options."""
        for _, real_estate in sorted(self.keyed, key=itemgetter(0)):
            yield real_estate

    @property
    def keyed(self):
        """Generates (<keys>, <real_estate>) tuples."""
        for orm, dom in self.real_estates:
            f_re = FilterableRealEstate(dom)
            keys = []

            for sort_option in self.sort_options:
                option, desc = sort_option
                option_func = OPTIONS.get(option)

                if option_func is None:
                    raise InvalidSortingOption(option)

                keys.append(Key(option_func(f_re), desc=desc))

            yield (keys, (orm, dom))
