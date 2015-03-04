"""Realtor and real estate filtering"""

from datetime import datetime
from openimmodb2.immobilie import Immobilie
from .lib import cast, Operators
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
              Operators.NI: lambda x, y: x not in y}


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
        return Immobilie.immobilie(self.user.cid)

    @property
    def immobilie(self):
        """Yields filteres real estates"""
        if self.user.ignore_restrictions:
            yield from self._immobilie
        else:
            for immobilie in self._immobilie:
                if immobilie.approve(core['name']):
                    yield immobilie
                else:
                    continue    # Restricted!

    @property
    def _sieve(self):
        """Returns an approriate real estate sieve"""
        return RealEstateSieve(self.immobilie, self._filters)

    def filter(self):
        """Returns valid, filtered real estates"""
        return self._sieve.immobilie


class FilterableRealtor():
    """Wrapper class for an OpenImmo™-anbieter
    that can be filtered by certain attributes
    """

    def __init__(self, anbieter):
        """Sets the appropriate OpenImmo™-immobilie"""
        self._anbieter = anbieter

    @property
    def anbieter(self):
        """Returns the the realtor"""
        return self._anbieter

    @property
    def openimmo_anid(self):
        """Returns the realtor's UUID"""
        return str(self.anbieter.openimmo_anid)

    @property
    def anbieternr(self):
        """Realtor identifier"""
        if self.anbieter.anbieternr:
            return str(self.anbieter.anbieternr)
        else:
            return None

    @property
    def firma(self):
        """Returns the company's name"""
        return str(self.anbieter.firma)


class RealtorSieve():
    """Class that sieves realtors of an
    OpenImmo™ document by certain filters
    """

    options = {'openimmo_anid': (str, lambda f, op, v: op(f.openimmo_anid, v)),
               'anbieternr': (str, lambda f, op, v: op(f.anbieternr, v)),
               'firma': lambda f, op, v: op(f.firma, v)}

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
            candidate = FilterableRealtor(anbieter)
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
                            result = option_func(candidate, operation_func,
                                                 value)
                        except (AttributeError, TypeError, ValueError):
                            raise SievingError(option, operation, raw_value)
                        else:
                            if not result:
                                match = False
                                break
            if match:
                yield anbieter


class FilterableRealEstate():
    """Wrapper class for an OpenImmo™-immobilie
    that can be filtered by certain attributes
    """

    def __init__(self, immobilie):
        """Sets the appropriate OpenImmo™-immobilie"""
        self._immobilie = immobilie

    @classmethod
    def fromopenimmo(cls, openimmo):
        """Yields filterable real estates from an OpenImmo™ document"""
        for anbieter in openimmo.andbieter:
            yield from cls.fromanbieter(anbieter)

    @classmethod
    def fromanbieter(cls, anbieter):
        """Yields filterable real estates from a realtor"""
        for immobilie in anbieter.immobilie:
            yield cls(immobilie)

    @property
    def immobilie(self):
        """Returns the appropriate immobilie"""
        return self._immobilie

    @property
    def objektart(self):
        """Returns the OpenImmo™oObjektart
        XXX: This can only be one for one real estate according to OpenImmo™
        """
        oa = self.immobilie.objektkategorie.objektart
        if oa.zimmer:
            return 'zimmer'
        elif oa.wohnung:
            return 'wohnung'
        elif oa.haus:
            return 'haus'
        elif oa.grundstueck:
            return 'grundstueck'
        elif oa.buero_praxen:
            return 'buero_praxen'
        elif oa.einzelhandel:
            return 'einzelhandel'
        elif oa.gastgewerbe:
            return 'gastgewerbe'
        elif oa.hallen_lager_prod:
            return 'hallen_lager_prod'
        elif oa.land_und_forstwirtschaft:
            return 'land_und_forstwirtschaft'
        elif oa.parken:
            return 'parken'
        elif oa.sonstige:
            return 'sonstige'
        elif oa.freizeitimmobilie_gewerblich:
            return 'freizeitimmobilie_gewerblich'
        elif oa.zinshaus_renditeobjekt:
            return 'zinshaus_renditeobjekt'

    @property
    def objekttypen(self):
        """Returns a generator for the object's types"""
        oa = self.immobilie.objektkategorie.objektart
        for zimmer in oa.zimmer:
            if zimmer.zimmertyp:
                yield str(zimmer.zimmertyp)
        for wohnung in oa.wohnung:
            if wohnung.wohnungtyp:
                yield str(wohnung.wohnungtyp)
        for haus in oa.haus:
            if haus.haustyp:
                yield str(haus.haustyp)
        for grundstueck in oa.grundstueck:
            if grundstueck.grundst_typ:
                yield str(grundstueck.grundst_typ)
        for buero_praxen in oa.buero_praxen:
            if buero_praxen.buero_typ:
                yield str(buero_praxen.buero_typ)
        for einzelhandel in oa.einzelhandel:
            if einzelhandel.handel_typ:
                yield str(einzelhandel.handel_typ)
        for gastgewerbe in oa.gastgewerbe:
            if gastgewerbe.gastgew_typ:
                str(gastgewerbe.gastgew_typ)
        for hallen_lager_prod in oa.hallen_lager_prod:
            if hallen_lager_prod.hallen_typ:
                yield str(hallen_lager_prod.hallen_typ)
        for land_und_forstwirtschaft in oa.land_und_forstwirtschaft:
            if land_und_forstwirtschaft.land_typ:
                yield str(land_und_forstwirtschaft.land_typ)
        for parken in oa.parken:
            if parken.parken_typ:
                yield str(parken.parken_typ)
        for sonstige in oa.sonstige:
            if sonstige.sonstige_typ:
                yield str(sonstige.sonstige_typ)
        for freizeitimmobilie_gewerblich in oa.freizeitimmobilie_gewerblich:
            if freizeitimmobilie_gewerblich.freizeit_typ:
                yield str(freizeitimmobilie_gewerblich.freizeit_typ)
        for zinshaus_renditeobjekt in oa.zinshaus_renditeobjekt:
            if zinshaus_renditeobjekt.zins_typ:
                yield str(zinshaus_renditeobjekt.zins_typ)

    @property
    def land(self):
        """Returns the country"""
        try:
            iso_land = self.immobilie.geo.land.iso_land
        except AttributeError:
            return None
        else:
            if iso_land is not None:
                return str(iso_land)
            else:
                return None

    @property
    def ort(self):
        """Returns the city"""
        if self.immobilie.geo.ort is not None:
            return str(self.immobilie.geo.ort)
        else:
            return None

    @property
    def ortsteil(self):
        """Returns the city's district"""
        if self.immobilie.geo.regionaler_zusatz is not None:
            return str(self.immobilie.geo.regionaler_zusatz)
        else:
            return None

    @property
    def plz(self):
        """Returns the ZIP code"""
        if self.immobilie.geo.plz is not None:
            return str(self.immobilie.geo.plz)
        else:
            return None

    @property
    def strasse(self):
        """Returns the ZIP code"""
        if self.immobilie.geo.strasse is not None:
            return str(self.immobilie.geo.strasse)
        else:
            return None

    @property
    def hausnummer(self):
        """Returns the house number"""
        if self.immobilie.geo.hausnummer is not None:
            return str(self.immobilie.geo.hausnummer)
        else:
            return None

    @property
    def zimmer(self):
        """Returns the number of rooms"""
        if self.immobilie.flaechen.anzahl_zimmer is not None:
            return float(self.immobilie.flaechen.anzahl_zimmer)
        else:
            return None

    @property
    def etage(self):
        """Returns the floor of the flat / room"""
        if self.immobilie.geo.etage is not None:
            return int(self.immobilie.geo.etage)
        else:
            return None

    @property
    def etagen(self):
        """Returns the number of floors of the building"""
        if self.immobilie.geo.anzahl_etagen is not None:
            return int(self.immobilie.geo.anzahl_etagen)
        else:
            return None

    @property
    def wohnflaeche(self):
        """Total living space"""
        try:
            wohnflaeche = self.immobilie.flaechen.wohnflaeche
        except AttributeError:
            return None
        else:
            if wohnflaeche is not None:
                return float(wohnflaeche)
            else:
                return None

    @property
    def grundstuecksflaeche(self):
        """Total property area"""
        try:
            grundstuecksflaeche = self.immobilie.flaechen.grundstuecksflaeche
        except AttributeError:
            return None
        else:
            if grundstuecksflaeche is not None:
                return float(grundstuecksflaeche)
            else:
                return None

    @property
    def balkone(self):
        """Amount of baconies"""
        try:
            anzahl_balkone = self.immobilie.flaechen.anzahl_balkone
        except AttributeError:
            return None
        else:
            if anzahl_balkone is not None:
                return float(anzahl_balkone)
            else:
                return None

    @property
    def terrassen(self):
        """Amount of terraces"""
        try:
            anzahl_terrassen = self.immobilie.flaechen.anzahl_terrassen
        except AttributeError:
            return None
        else:
            if anzahl_terrassen is not None:
                return float(anzahl_terrassen)
            else:
                return None

    @property
    def kaltmiete(self):
        """Return the price of the cold rent"""
        try:
            kaltmiete = self.immobilie.preise.kaltmiete
        except AttributeError:
            return None
        else:
            if kaltmiete is not None:
                return float(kaltmiete)
            else:
                return None

    @property
    def warmmiete(self):
        """Returns the price of the warm rent"""
        try:
            warmmiete = self.immobilie.preise.warmmiete
        except AttributeError:
            return None
        else:
            return float(warmmiete) if warmmiete else None

    @property
    def nebenkosten(self):
        """Returns the price of the ancillary expenses"""
        try:
            nebenkosten = self.immobilie.preise.nebenkosten
        except AttributeError:
            return None
        else:
            return float(nebenkosten) if nebenkosten else None

    @property
    def kaufpreis(self):
        """Returns the purchase price"""
        try:
            kaufpreis = self.immobilie.preise.kaufpreis
        except AttributeError:
            return None
        else:
            return float(kaufpreis) if kaufpreis else None

    @property
    def pacht(self):
        """Returns the lease price"""
        try:
            pacht = self.immobilie.preise.pacht
        except AttributeError:
            return None
        else:
            return float(pacht) if pacht else None

    @property
    def erbpacht(self):
        """Returns the emphyteusis price"""
        try:
            erbpacht = self.immobilie.preise.erbpacht
        except AttributeError:
            return None
        else:
            return float(erbpacht) if erbpacht else None

    @property
    def aussen_courtage(self):
        """External finder's fee"""
        try:
            aussen_courtage = self.immobilie.preise.aussen_courtage
        except AttributeError:
            return None
        else:
            return str(aussen_courtage) if aussen_courtage else None

    @property
    def innen_courtage(self):
        """Internal finder's fee"""
        try:
            innen_courtage = self.immobilie.preise.innen_courtage
        except AttributeError:
            return None
        else:
            return str(innen_courtage) if innen_courtage else None

    @property
    def openimmo_obid(self):
        """Returns the UUID of the real estate"""
        return str(self.immobilie.verwaltung_techn.openimmo_obid)

    @property
    def objektnr_intern(self):
        """Returns the internal identifier of the real estate"""
        if self.immobilie.verwaltung_techn.objektnr_intern:
            return str(self.immobilie.verwaltung_techn.objektnr_intern)
        else:
            return None

    @property
    def objektnr_extern(self):
        """Returns the external identifier of the real estate"""
        return str(self.immobilie.verwaltung_techn.objektnr_extern)

    @property
    def barrierefrei(self):
        """Returns whether the real estate is considered barrier free"""
        try:
            return bool(self.immobilie.ausstattung.barrierefrei)
        except AttributeError:
            return False

    @property
    def haustiere(self):
        """Returns pets allowed flag"""
        try:
            return bool(self.immobilie.verwaltung_objekt.haustiere)
        except AttributeError:
            return False

    @property
    def raucher(self):
        """Returns flag whether smoking is allowed"""
        try:
            return not bool(self.immobilie.verwaltung_objekt.nichtraucher)
        except AttributeError:
            return True

    @property
    def kaufbar(self):
        """Returns whether the real estate is for sale"""
        return bool(self.immobilie.objektkategorie.vermarktungsart.KAUF)

    @property
    def mietbar(self):
        """Returns whether the real estate is for rent"""
        return bool(self.immobilie.objektkategorie.vermarktungsart.MIETE_PACHT)

    @property
    def erbpachtbar(self):
        """Returns whether the real estate is for emphyteusis"""
        return bool(self.immobilie.objektkategorie.vermarktungsart.ERBPACHT)

    @property
    def leasing(self):
        """Returns whether the real estate is for leasing"""
        return bool(self.immobilie.objektkategorie.vermarktungsart.LEASING)

    @property
    def verfuegbar_ab(self):
        """Returns from when on the real estate is obtainable"""
        if self.immobilie.verwaltung_objekt.verfuegbar_ab:
            return str(self.immobilie.verwaltung_objekt.verfuegbar_ab)
        else:
            return None

    @property
    def abdatum(self):
        """Returns a date from when on the real estate is obtainable"""
        if self.immobilie.verwaltung_objekt.abdatum:
            return datetime(self.immobilie.verwaltung_objekt.abdatum)
        else:
            return None

    @property
    def moebliert(self):
        """Returns whether and if how the real estate is furnished"""
        if self.immobilie.ausstattung.moebliert:
            if self.immobilie.ausstattung.moebliert.moeb:
                return str(self.immobilie.ausstattung.moebliert.moeb)
            else:
                return True
        else:
            return False

    @property
    def seniorengerecht(self):
        """Returns whether the real estate is senior-freindly"""
        try:
            return bool(self.immobilie.ausstattung.seniorengerecht)
        except AttributeError:
            return False

    @property
    def baujahr(self):
        """Returns the year of construction"""
        try:
            baujahr = self.immobilie.zustand_angaben.baujahr
        except AttributeError:
            return None
        else:
            return str(baujahr) if baujahr else None

    @property
    def zustand(self):
        """Returns the condition of the real estate"""
        try:
            zustand = self.immobilie.zustand_angaben.zustand.zustand_art
        except AttributeError:
            return None
        else:
            return str(zustand) if zustand else None

    @property
    def epart(self):
        """Returns the energy certificate type"""
        try:
            epart = self.immobilie.zustand_angaben.energiepass.epart
        except AttributeError:
            return None
        else:
            return str(epart) if epart else None

    @property
    def energieverbrauchkennwert(self):
        """Returns the energy consumption characteristic value"""
        try:
            energieverbrauchkennwert = (self.immobilie.zustand_angaben
                                        .energiepass.energieverbrauchkennwert)
        except AttributeError:
            return None
        else:
            if energieverbrauchkennwert:
                return str(energieverbrauchkennwert)
            else:
                return None

    @property
    def endenergiebedarf(self):
        """Returns the energy consumption value"""
        try:
            endenergiebedarf = (self.immobilie.zustand_angaben
                                .energiepass.endenergiebedarf)
        except AttributeError:
            return None
        else:
            return str(endenergiebedarf) if endenergiebedarf else None

    @property
    def primaerenergietraeger(self):
        """Returns the energy certificate type"""
        try:
            primaerenergietraeger = (self.immobilie.zustand_angaben
                                     .energiepass.primaerenergietraeger)
        except AttributeError:
            return None
        else:
            if primaerenergietraeger:
                return str(primaerenergietraeger)
            else:
                return None

    @property
    def stromwert(self):
        """Returns the electricity value"""
        try:
            stromwert = self.immobilie.zustand_angaben.energiepass.stromwert
        except AttributeError:
            return None
        else:
            return str(stromwert) if stromwert else None

    @property
    def waermewert(self):
        """Returns the heating value"""
        try:
            waermewert = self.immobilie.zustand_angaben.energiepass.waermewert
        except AttributeError:
            return None
        else:
            return str(waermewert) if waermewert else None

    @property
    def wertklasse(self):
        """Returns the value class"""
        try:
            wertklasse = self.immobilie.zustand_angaben.energiepass.wertklasse
        except AttributeError:
            return None
        else:
            return str(wertklasse) if wertklasse else None

    @property
    def min_mietdauer(self):
        """Minimum rental time"""
        try:
            min_mietdauer = self.immobilie.verwaltung_objekt.min_mietdauer
        except AttributeError:
            return None
        else:
            if min_mietdauer:
                if min_mietdauer.min_dauer:
                    return ' '.join([str(min_mietdauer),
                                     str(min_mietdauer.min_dauer)])
                else:
                    return str(min_mietdauer)
            else:
                return None

    @property
    def max_mietdauer(self):
        """Maximum rental time"""
        try:
            max_mietdauer = self.immobilie.verwaltung_objekt.max_mietdauer
        except AttributeError:
            return None
        else:
            if max_mietdauer:
                if max_mietdauer.max_dauer:
                    return ' '.join([str(max_mietdauer),
                                     str(max_mietdauer.max_dauer)])
                else:
                    return str(max_mietdauer)
            else:
                return None

    @property
    def laufzeit(self):
        """Remaining time of emphyteusis"""
        try:
            laufzeit = self.immobilie.verwaltung_objekt.laufzeit
        except AttributeError:
            return None
        else:
            return float(laufzeit) if laufzeit else None

    @property
    def max_personen(self):
        """Maximum amount of persons"""
        try:
            max_personen = self.immobilie.verwaltung_objekt.max_personen
        except AttributeError:
            return None
        else:
            return int(max_personen) if max_personen else None


class RealEstateSieve():
    """Class that sieves real estates
    of a realtor by certain filters
    """

    options = {'objektart': lambda f, op, v: op(f.objektart, v),
               'objekttyp': lambda f, op, v: op(v, f.objekttypen),
               'land': lambda f, op, v: op(f.land, v),
               'ort': lambda f, op, v: op(f.ort, v),
               'ortsteil': lambda f, op, v: op(f.ortsteil, v),
               'plz': lambda f, op, v: op(f.plz, v),
               'strasse': lambda f, op, v: op(f.strasse, v),
               'hausnummer': lambda f, op, v: op(f.hausnummer, v),
               'zimmer': lambda f, op, v: op(f.zimmer, v),
               'etage': lambda f, op, v: op(f.etage, v),
               'etagen': lambda f, op, v: op(f.etagen, v),
               'wohnflaeche': lambda f, op, v: op(f.wohnflaeche, v),
               'grundstuecksflaeche':
                   lambda f, op, v: op(f.grundstuecksflaeche, v),
               'balkone': lambda f, op, v: op(f.balkone, v),
               'terrassen': lambda f, op, v: op(f.terrassen, v),
               'kaltmiete': lambda f, op, v: op(f.kaltmiete, v),
               'warmmiete': lambda f, op, v: op(f.warmmiete, v),
               'nebenkosten': lambda f, op, v: op(f.nebenkosten, v),
               'kaufpreis': lambda f, op, v: op(f.kaufpreis, v),
               'pacht': lambda f, op, v: op(f.pacht, v),
               'erbpacht': lambda f, op, v: op(f.erbpacht, v),
               'aussen_courtage': lambda f, op, v: op(f.aussen_courtage, v),
               'innen_courtage': lambda f, op, v: op(f.innen_courtage, v),
               'openimmo_obid':
                   (str, lambda f, op, v: op(f.openimmo_obid, v)),
               'objektnr_intern':
                   (str, lambda f, op, v: op(f.objektnr_intern, v)),
               'objektnr_extern':
                   (str, lambda f, op, v: op(f.objektnr_extern, v)),
               'barrierefrei': lambda f, op, v: op(f.barrierefrei, v),
               'haustiere': lambda f, op, v: op(f.haustiere, v),
               'raucher': lambda f, op, v: op(f.raucher, v),
               'kaufbar': lambda f, op, v: op(f.kaufbar, v),
               'mietbar': lambda f, op, v: op(f.mietbar, v),
               'erbpachtbar': lambda f, op, v: op(f.erbpachtbar, v),
               'leasing': lambda f, op, v: op(f.leasing, v),
               'verfuegbar_ab': lambda f, op, v: op(f.verfuegbar_ab, v),
               'abdatum': lambda f, op, v: op(f.abdatum, v),
               'moebliert': lambda f, op, v: op(f.moebliert, v),
               'seniorengerecht': lambda f, op, v: op(f.seniorengerecht, v),
               'baujahr': (str, lambda f, op, v: op(f.baujahr, v)),
               'zustand': lambda f, op, v: op(f.zustand, v),
               'epart': lambda f, op, v: op(f.epart, v),
               'energieverbrauchkennwert':
                   lambda f, op, v: op(f.energieverbrauchkennwert, v),
               'endenergiebedarf': lambda f, op, v: op(f.endenergiebedarf, v),
               'primaerenergietraeger':
                   lambda f, op, v: op(f.primaerenergietraeger, v),
               'stromwert': lambda f, op, v: op(f.stromwert, v),
               'waermewert': lambda f, op, v: op(f.waermewert, v),
               'wertklasse': lambda f, op, v: op(f.wertklasse, v),
               'min_mietdauer': lambda f, op, v: op(f.min_mietdauer, v),
               'max_mietdauer': lambda f, op, v: op(f.max_mietdauer, v),
               'laufzeit': lambda f, op, v: op(f.laufzeit, v),
               'max_personen': lambda f, op, v: op(f.max_personen, v)}

    def __init__(self, real_estates, filters):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>)
        """
        self._real_estates = real_estates
        self._filters = filters

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def filters(self):
        """Returns the filters"""
        return self._filters

    @property
    def immobilie(self):
        """Property alias to sieve()"""
        return self.sieve()

    def sieve(self):
        """Sieve real estates by the given filters"""
        for immobilie in self.real_estates:
            candidate = FilterableRealEstate(immobilie)
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
                            result = option_func(candidate, operation_func,
                                                 value)
                        except (AttributeError, TypeError, ValueError):
                            raise SievingError(option, operation, raw_value)
                        else:
                            if not result:
                                match = False
                                break
            if match:
                yield immobilie
