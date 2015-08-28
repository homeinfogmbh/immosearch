"""Realtor and real estate filtering"""

from homeinfo.lib.boolparse import SecurityError, BooleanEvaluator
from openimmodb3.db import Immobilie

from .lib import RealEstateWrapper
from .errors import SecurityBreach

__all__ = ['UserRealEstateSieve']


class RealEstateSieve():
    """Class that sieves real estates by certain filters"""

    options = {
        'objektart': lambda f: f.objektart,
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
        'kaltmiete': lambda f: f.kaltmiete or f.nettokaltmiete,
        'warmmiete': lambda f: f.warmmiete or f.gesamtmiete,
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
        'rollstuhlgerecht': lambda f: f.rollstuhlgerecht,
        'haustiere': lambda f: f.haustiere,
        'raucher': lambda f: f.raucher,
        'kaufbar': lambda f: f.kaufbar,
        'mietbar': lambda f: f.mietbar,
        'erbpachtbar': lambda f: f.erbpachtbar,
        'leasing': lambda f: f.leasing,
        'verfuegbar_ab': lambda f: f.verfuegbar_ab,
        'abdatum': lambda f: f.abdatum,
        'moebliert': lambda f: f.moebliert,
        'seniorengerecht': lambda f: f.seniorengerecht,
        'baujahr': (str, lambda f: f.baujahr),
        'zustand': lambda f: f.zustand,
        'epart': lambda f: f.epart,
        'energieverbrauchkennwert': lambda f: f.energieverbrauchkennwert,
        'endenergiebedarf': lambda f: f.endenergiebedarf,
        'primaerenergietraeger': lambda f: f.primaerenergietraeger,
        'stromwert': lambda f: f.stromwert,
        'waermewert': lambda f: f.waermewert,
        'wertklasse': lambda f: f.wertklasse,
        'min_mietdauer': lambda f: f.min_mietdauer,
        'max_mietdauer': lambda f: f.max_mietdauer,
        'laufzeit': lambda f: f.laufzeit,
        'max_personen': lambda f: f.max_personen
    }

    def __init__(self, real_estates, filters):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>)
        """
        self._real_estates = real_estates
        self._filters = filters

    def __iter__(self):
        """Sieve real estates by the given filters"""
        if self._filters:
            for real_estate in self.real_estates:
                wrapped_real_estate = RealEstateWrapper(real_estate)
                be = BooleanEvaluator(
                    self._filters, callback=wrapped_real_estate.evaluate)
                try:
                    if be:
                        yield real_estate
                except SecurityError as sec_err:
                    raise SecurityBreach(str(sec_err)) from None
        else:
            yield from self.real_estates

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def filters(self):
        """Returns the filters"""
        return self._filters


class UserRealEstateSieve(RealEstateSieve):
    """Class that sieves real estates of a user"""

    def __init__(self, user, filters):
        """Initializes super class with the user's real estates"""
        super().__init__(
            (i.immobilie for i in Immobilie.by_cid(user.cid)),
            filters)
        self._user = user

    @property
    def user(self):
        """Returns the user"""
        return self._user
