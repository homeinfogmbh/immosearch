"""Realtor and real estate filtering"""

from openimmodb2.db import Immobilie
from .lib import cast, Operators, Realtor, RealEstate
from .errors import FilterOperationNotImplemented, InvalidFilterOption,\
    SievingError
from .config import core

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['UserFilter']

operations = {Operators.EQ: lambda x, y: x == y,
              # Operators.EG: ,
              Operators.EC: lambda x, y: x.lower() == y.lower(),
              Operators.NE: lambda x, y: x != y,
              # Operators.NG: ,
              Operators.NC: lambda x, y: x.lower() != y.lower(),
              Operators.LT: lambda x, y: x < y,
              Operators.LE: lambda x, y: x <= y,
              Operators.GT: lambda x, y: x > y,
              Operators.GE: lambda x, y: x >= y,
              Operators.IN: lambda x, y: x in y,
              Operators.NI: lambda x, y: x not in y,
              Operators.CO: lambda x, y: y in x,
              Operators.CN: lambda x, y: y not in x}


class UserFilter():
    """Class that filters real estates of a user"""

    def __init__(self, user, filters):
        """Initializes with a user record"""
        self._user = user
        self._filters = filters

    @property
    def user(self):
        """Returns the user record"""
        return self._user

    @property
    def _immobilie(self):
        """Returns valid, unfiltered real estates"""
        for i in Immobilie.by_cid(self.user.cid):
            yield i.immobilie

    @property
    def immobilie(self):
        """Yields filtered real estates"""
        if self.user.ignore_restrictions:
            yield from self._immobilie
        else:
            for immobilie in self._immobilie:
                if immobilie.approve(core['name']):
                    yield immobilie

    @property
    def _sieve(self):
        """Returns an appropriate real estate sieve"""
        return RealEstateSieve(self.immobilie, self._filters)

    def filter(self):
        """Returns valid, filtered real estates"""
        return self._sieve.sieve()


class RealtorSieve():
    """Class that sieves realtors of an
    OpenImmo™ document by certain filters
    """

    options = {'openimmo_anid': (str, lambda f: f.openimmo_anid),
               'anbieternr': (str, lambda f: f.anbieternr),
               'firma': lambda f: f.firma}

    def __init__(self, openimmo, filters):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>)
        """
        self._openimmo = openimmo
        self._filters = filters

    @property
    def openimmo(self):
        """Returns the realtor"""
        return self._openimmo

    @property
    def filters(self):
        """Returns the filters"""
        return self._filters

    @property
    def anbieter(self):
        """Property alias to sieve()"""
        return self.sieve()

    def sieve(self):
        """Sieve real estates by the given filters"""
        for anbieter in self.openimmo.anbieter:
            candidate = Realtor(anbieter)
            match = True
            for f in self.filters:
                option, operation, raw_value = f
                operation_func = operations.get(operation)
                if operation_func is None:
                    raise FilterOperationNotImplemented(operation)
                else:
                    option_ = self.options.get(option)
                    if option_ is None:
                        raise InvalidFilterOption(option)
                    else:
                        try:
                            option_format, option_func = option_
                        except TypeError:
                            option_format = None
                            option_func = option_
                        value = cast(raw_value, typ=option_format)
                        try:
                            result = operation_func(option_func(candidate),
                                                    value)
                        except (AttributeError, TypeError, ValueError):
                            raise SievingError(option, operation, raw_value)
                        else:
                            if not result:
                                match = False
                                break
            if match:
                yield anbieter


class RealEstateSieve():
    """Class that sieves real estates
    of a realtor by certain filters
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
               'verfuegbar_ab': lambda f: f.verfuegbar_ab,
               'abdatum': lambda f: f.abdatum,
               'moebliert': lambda f: f.moebliert,
               'seniorengerecht': lambda f: f.seniorengerecht,
               'baujahr': (str, lambda f: f.baujahr),
               'zustand': lambda f: f.zustand,
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

    def __init__(self, immobilie, filters):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>)
        """
        self._immobilie = immobilie
        self._filters = filters

    @property
    def filters(self):
        """Returns the filters"""
        return self._filters

    @property
    def immobilie(self):
        """Property alias to sieve()"""
        return self._immobilie

    def sieve(self):
        """Sieve real estates by the given filters"""
        for immobilie in self.immobilie:
            real_estate = RealEstate(immobilie)
            match = True
            for f in self.filters:
                option, operation, raw_value = f
                operation_func = operations.get(operation)
                if operation_func is None:
                    raise FilterOperationNotImplemented(operation)
                else:
                    option_ = self.options.get(option)
                    if option_ is None:
                        raise InvalidFilterOption(option)
                    else:
                        try:
                            option_format, option_func = option_
                        except TypeError:
                            option_format = None
                            option_func = option_
                        value = cast(raw_value, typ=option_format)
                        try:
                            result = operation_func(option_func(real_estate),
                                                    value)
                        except (AttributeError, TypeError, ValueError):
                            raise SievingError(option, operation, raw_value)
                        else:
                            if not result:
                                match = False
                                break
            if match:
                yield immobilie
