"""Realtor and real estate filtering."""

from datetime import datetime

from boolparse import SecurityError, evaluate

from .lib import cast, Operators
from .errors import SecurityBreach, InvalidFilterOption,\
    FilterOperationNotImplemented, SievingError

__all__ = ['RealEstateSieve']


OPERATIONS = {
    Operators.EQ.value: lambda x, y: x == y,
    # Operators.EG.value: ,
    Operators.EC.value: lambda x, y: x.lower() == y.lower(),
    Operators.NE.value: lambda x, y: x != y,
    # Operators.NG.value: ,
    Operators.NC.value: lambda x, y: x.lower() != y.lower(),
    Operators.LT.value: lambda x, y: x < y,
    Operators.LE.value: lambda x, y: x <= y,
    Operators.GT.value: lambda x, y: x > y,
    Operators.GE.value: lambda x, y: x >= y,
    Operators.IN.value: lambda x, y: x in y,
    Operators.NI.value: lambda x, y: x not in y,
    Operators.CO.value: lambda x, y: y in x,
    Operators.CN.value: lambda x, y: y not in x}

OPTIONS = {
    'objektart': lambda fre: fre.objektart,
    'objekttyp': lambda fre: fre.objekttypen,
    'land': lambda fre: fre.land,
    'ort': lambda fre: fre.ort,
    'ortsteil': lambda fre: fre.ortsteil,
    'plz': lambda fre: fre.plz,
    'strasse': lambda fre: fre.strasse,
    'hausnummer': lambda fre: fre.hausnummer,
    'zimmer': lambda fre: fre.zimmer,
    'etage': lambda fre: fre.etage,
    'etagen': lambda fre: fre.etagen,
    'wohnflaeche': lambda fre: fre.wohnflaeche,
    'grundstuecksflaeche': lambda fre: fre.grundstuecksflaeche,
    'balkone': lambda fre: fre.balkone,
    'terrassen': lambda fre: fre.terrassen,
    'kaltmiete': lambda fre: fre.kaltmiete or fre.nettokaltmiete,
    'warmmiete': lambda fre: fre.warmmiete or fre.gesamtmiete,
    'nebenkosten': lambda fre: fre.nebenkosten,
    'kaufpreis': lambda fre: fre.kaufpreis,
    'pacht': lambda fre: fre.pacht,
    'erbpacht': lambda fre: fre.erbpacht,
    'aussen_courtage': lambda fre: fre.aussen_courtage,
    'innen_courtage': lambda fre: fre.innen_courtage,
    'openimmo_obid': (str, lambda fre: fre.openimmo_obid),
    'objektnr_intern': (str, lambda fre: fre.objektnr_intern),
    'objektnr_extern': (str, lambda fre: fre.objektnr_extern),
    'barrierefrei': lambda fre: fre.barrierefrei,
    'rollstuhlgerecht': lambda fre: fre.rollstuhlgerecht,
    'haustiere': lambda fre: fre.haustiere,
    'raucher': lambda fre: fre.raucher,
    'kaufbar': lambda fre: fre.kaufbar,
    'mietbar': lambda fre: fre.mietbar,
    'erbpachtbar': lambda fre: fre.erbpachtbar,
    'leasing': lambda fre: fre.leasing,
    'verfuegbar_ab': lambda fre: fre.verfuegbar_ab,
    'abdatum': lambda fre: fre.abdatum,
    'moebliert': lambda fre: fre.moebliert,
    'seniorengerecht': lambda fre: fre.seniorengerecht,
    'baujahr': (str, lambda fre: fre.baujahr),
    'zustand': lambda fre: fre.zustand,
    'epart': lambda fre: fre.epart,
    'energieverbrauchkennwert': lambda fre: fre.energieverbrauchkennwert,
    'endenergiebedarf': lambda fre: fre.endenergiebedarf,
    'primaerenergietraeger': lambda fre: fre.primaerenergietraeger,
    'stromwert': lambda fre: fre.stromwert,
    'waermewert': lambda fre: fre.waermewert,
    'wertklasse': lambda fre: fre.wertklasse,
    'min_mietdauer': lambda fre: fre.min_mietdauer,
    'max_mietdauer': lambda fre: fre.max_mietdauer,
    'laufzeit': lambda fre: fre.laufzeit,
    'max_personen': lambda fre: fre.max_personen,
    'weitergabe_generell': lambda fre: fre.weitergabe_generell,
    'weitergabe_negativ': lambda fre: fre.weitergabe_negativ,
    'weitergabe_positiv': lambda fre: fre.weitergabe_positiv,
    'aktiv': lambda fre: fre.active}


class DontCare(Exception):
    """Indicates that a filtering option
    does not care for the compared value.
    """

    def __init__(self, val):
        """Sets the avaluated boolean value."""
        super().__init__(val)
        self._val = val

    def __bool__(self):
        """Returns the value"""
        return self._val


class FilterableRealEstate:
    """Wrapper class for an OpenImmo™-immobilie
    that can be filtered by certain attributes.
    """

    def __init__(self, immobilie):
        """Sets the appropriate OpenImmo™-immobilie"""
        self.immobilie = immobilie

    @classmethod
    def fromopenimmo(cls, openimmo):
        """Yields filterable real estates from an OpenImmo document."""
        for anbieter in openimmo.andbieter:
            for filterable_real_estate in cls.fromanbieter(anbieter):
                yield filterable_real_estate

    @classmethod
    def fromanbieter(cls, anbieter):
        """Yields filterable real estates from a realtor."""
        for immobilie in anbieter.immobilie:
            yield cls(immobilie)

    @property
    def objektart(self):
        """Returns the OpenImmo-Objektart."""
        objektart = self.immobilie.objektkategorie.objektart

        if objektart.zimmer:
            return 'zimmer'
        elif objektart.wohnung:
            return 'wohnung'
        elif objektart.haus:
            return 'haus'
        elif objektart.grundstueck:
            return 'grundstueck'
        elif objektart.buero_praxen:
            return 'buero_praxen'
        elif objektart.einzelhandel:
            return 'einzelhandel'
        elif objektart.gastgewerbe:
            return 'gastgewerbe'
        elif objektart.hallen_lager_prod:
            return 'hallen_lager_prod'
        elif objektart.land_und_forstwirtschaft:
            return 'land_und_forstwirtschaft'
        elif objektart.parken:
            return 'parken'
        elif objektart.sonstige:
            return 'sonstige'
        elif objektart.freizeitimmobilie_gewerblich:
            return 'freizeitimmobilie_gewerblich'
        elif objektart.zinshaus_renditeobjekt:
            return 'zinshaus_renditeobjekt'

    @property
    def objekttypen(self):
        """Returns a generator for the object's types."""
        objektart = self.immobilie.objektkategorie.objektart

        for zimmer in objektart.zimmer:
            if zimmer.zimmertyp:
                yield str(zimmer.zimmertyp)
        for wohnung in objektart.wohnung:
            if wohnung.wohnungtyp:
                yield str(wohnung.wohnungtyp)
        for haus in objektart.haus:
            if haus.haustyp:
                yield str(haus.haustyp)
        for grundstueck in objektart.grundstueck:
            if grundstueck.grundst_typ:
                yield str(grundstueck.grundst_typ)
        for buero_praxen in objektart.buero_praxen:
            if buero_praxen.buero_typ:
                yield str(buero_praxen.buero_typ)
        for einzelhandel in objektart.einzelhandel:
            if einzelhandel.handel_typ:
                yield str(einzelhandel.handel_typ)
        for gastgewerbe in objektart.gastgewerbe:
            if gastgewerbe.gastgew_typ:
                yield str(gastgewerbe.gastgew_typ)
        for hallen_lager_prod in objektart.hallen_lager_prod:
            if hallen_lager_prod.hallen_typ:
                yield str(hallen_lager_prod.hallen_typ)
        for land_und_forstwirtschaft in objektart.land_und_forstwirtschaft:
            if land_und_forstwirtschaft.land_typ:
                yield str(land_und_forstwirtschaft.land_typ)
        for parken in objektart.parken:
            if parken.parken_typ:
                yield str(parken.parken_typ)
        for sonstige in objektart.sonstige:
            if sonstige.sonstige_typ:
                yield str(sonstige.sonstige_typ)
        for freizeitimmobilie_gewerblich in \
                objektart.freizeitimmobilie_gewerblich:
            if freizeitimmobilie_gewerblich.freizeit_typ:
                yield str(freizeitimmobilie_gewerblich.freizeit_typ)
        for zinshaus_renditeobjekt in objektart.zinshaus_renditeobjekt:
            if zinshaus_renditeobjekt.zins_typ:
                yield str(zinshaus_renditeobjekt.zins_typ)

    @property
    def land(self):
        """Returns the country."""
        try:
            iso_land = self.immobilie.geo.land.iso_land
        except AttributeError:
            return None
        else:
            if iso_land is not None:
                return str(iso_land)

    @property
    def ort(self):
        """Returns the city."""
        if self.immobilie.geo.ort is not None:
            return str(self.immobilie.geo.ort)

    @property
    def ortsteil(self):
        """Returns the city's district."""
        if self.immobilie.geo.regionaler_zusatz is not None:
            return str(self.immobilie.geo.regionaler_zusatz)

    @property
    def plz(self):
        """Returns the ZIP code."""
        if self.immobilie.geo.plz is not None:
            return str(self.immobilie.geo.plz)

    @property
    def strasse(self):
        """Returns the ZIP code."""
        if self.immobilie.geo.strasse is not None:
            return str(self.immobilie.geo.strasse)

    @property
    def hausnummer(self):
        """Returns the house number."""
        if self.immobilie.geo.hausnummer is not None:
            return str(self.immobilie.geo.hausnummer)

    @property
    def zimmer(self):
        """Returns the number of rooms."""
        if self.immobilie.flaechen.anzahl_zimmer is not None:
            return float(self.immobilie.flaechen.anzahl_zimmer)

    @property
    def etage(self):
        """Returns the floor of the flat / room."""
        if self.immobilie.geo.etage is not None:
            return int(self.immobilie.geo.etage)

    @property
    def etagen(self):
        """Returns the number of floors of the building."""
        if self.immobilie.geo.anzahl_etagen is not None:
            return int(self.immobilie.geo.anzahl_etagen)

    @property
    def wohnflaeche(self):
        """Total living space."""
        try:
            wohnflaeche = self.immobilie.flaechen.wohnflaeche
        except AttributeError:
            return None
        else:
            if wohnflaeche is not None:
                return float(wohnflaeche)

    @property
    def grundstuecksflaeche(self):
        """Total property area."""
        try:
            grundstuecksflaeche = self.immobilie.flaechen.grundstuecksflaeche
        except AttributeError:
            return None
        else:
            if grundstuecksflaeche is not None:
                return float(grundstuecksflaeche)

    @property
    def balkone(self):
        """Amount of balconies."""
        try:
            anzahl_balkone = self.immobilie.flaechen.anzahl_balkone
        except AttributeError:
            return None
        else:
            if anzahl_balkone is not None:
                return float(anzahl_balkone)

    @property
    def terrassen(self):
        """Amount of terraces."""
        try:
            anzahl_terrassen = self.immobilie.flaechen.anzahl_terrassen
        except AttributeError:
            return None
        else:
            if anzahl_terrassen is not None:
                return float(anzahl_terrassen)

    @property
    def kaltmiete(self):
        """Return the price of the cold rent."""
        try:
            kaltmiete = self.immobilie.preise.kaltmiete
        except AttributeError:
            return None
        else:
            return float(kaltmiete) if kaltmiete else None

    @property
    def nettokaltmiete(self):
        """Returns the net value of the cold rent."""
        try:
            nettokaltmiete = self.immobilie.preise.nettokaltmiete
        except AttributeError:
            return None
        else:
            return float(nettokaltmiete) if nettokaltmiete else None

    @property
    def warmmiete(self):
        """Returns the price of the warm rent."""
        try:
            warmmiete = self.immobilie.preise.warmmiete
        except AttributeError:
            return None
        else:
            return float(warmmiete) if warmmiete else None

    @property
    def gesamtmiete(self):
        """Returns the total rent."""
        if self.kaltmiete:
            result = self.kaltmiete
        else:
            result = self.nettokaltmiete

        if result:
            if self.nebenkosten:
                result += self.nebenkosten

            if not self.immobilie.preise.heizkosten_enthalten:
                if self.heizkosten:
                    result += self.heizkosten
        else:
            result = self.warmmiete

        return result

    @property
    def nebenkosten(self):
        """Returns the price of the ancillary expenses."""
        try:
            nebenkosten = self.immobilie.preise.nebenkosten
        except AttributeError:
            return None
        else:
            return float(nebenkosten) if nebenkosten else None

    @property
    def heizkosten(self):
        """Returns the heating costs."""
        try:
            heizkosten = self.immobilie.preise.heizkosten
        except AttributeError:
            return None
        else:
            return float(heizkosten) if heizkosten else None

    @property
    def kaufpreis(self):
        """Returns the purchase price."""
        try:
            kaufpreis = self.immobilie.preise.kaufpreis
        except AttributeError:
            return None
        else:
            return float(kaufpreis) if kaufpreis else None

    @property
    def pacht(self):
        """Returns the lease price."""
        try:
            pacht = self.immobilie.preise.pacht
        except AttributeError:
            return None
        else:
            return float(pacht) if pacht else None

    @property
    def erbpacht(self):
        """Returns the emphyteusis price."""
        try:
            erbpacht = self.immobilie.preise.erbpacht
        except AttributeError:
            return None
        else:
            return float(erbpacht) if erbpacht else None

    @property
    def aussen_courtage(self):
        """External finder's fee."""
        try:
            aussen_courtage = self.immobilie.preise.aussen_courtage
        except AttributeError:
            return None
        else:
            return str(aussen_courtage) if aussen_courtage else None

    @property
    def innen_courtage(self):
        """Internal finder's fee."""
        try:
            innen_courtage = self.immobilie.preise.innen_courtage
        except AttributeError:
            return None
        else:
            return str(innen_courtage) if innen_courtage else None

    @property
    def openimmo_obid(self):
        """Returns the UUID of the real estate."""
        return str(self.immobilie.verwaltung_techn.openimmo_obid)

    @property
    def objektnr_intern(self):
        """Returns the internal identifier of the real estate."""
        if self.immobilie.verwaltung_techn.objektnr_intern:
            return str(self.immobilie.verwaltung_techn.objektnr_intern)

    @property
    def objektnr_extern(self):
        """Returns the external identifier of the real estate."""
        return str(self.immobilie.verwaltung_techn.objektnr_extern)

    @property
    def barrierefrei(self):
        """Returns whether the real estate is considered barrier free."""
        try:
            return bool(self.immobilie.ausstattung.barrierefrei)
        except AttributeError:
            return False

    @property
    def rollstuhlgerecht(self):
        """Returns whether the real estate is wheelchair-
        compatible aka 'limited barrier free'.
        """
        try:
            return bool(self.immobilie.ausstattung.rollstuhlgerecht)
        except AttributeError:
            return False

    @property
    def haustiere(self):
        """Returns pets allowed flag."""
        try:
            return bool(self.immobilie.verwaltung_objekt.haustiere)
        except AttributeError:
            return False

    @property
    def raucher(self):
        """Returns flag whether smoking is allowed."""
        try:
            return not bool(self.immobilie.verwaltung_objekt.nichtraucher)
        except AttributeError:
            return True

    @property
    def kaufbar(self):
        """Returns whether the real estate is for sale."""
        return bool(self.immobilie.objektkategorie.vermarktungsart.KAUF)

    @property
    def mietbar(self):
        """Returns whether the real estate is for rent."""
        return bool(self.immobilie.objektkategorie.vermarktungsart.MIETE_PACHT)

    @property
    def erbpachtbar(self):
        """Returns whether the real estate is for emphyteusis."""
        return bool(self.immobilie.objektkategorie.vermarktungsart.ERBPACHT)

    @property
    def leasing(self):
        """Returns whether the real estate is for leasing."""
        return bool(self.immobilie.objektkategorie.vermarktungsart.LEASING)

    @property
    def verfuegbar_ab(self):
        """Returns from when on the real estate is obtainable."""
        if self.immobilie.verwaltung_objekt.verfuegbar_ab:
            return str(self.immobilie.verwaltung_objekt.verfuegbar_ab)

    @property
    def abdatum(self):
        """Returns a date from when on the real estate is obtainable."""
        if self.immobilie.verwaltung_objekt.abdatum:
            return datetime(self.immobilie.verwaltung_objekt.abdatum)

    @property
    def moebliert(self):
        """Returns whether and if how the real estate is furnished."""
        if self.immobilie.ausstattung.moebliert:
            if self.immobilie.ausstattung.moebliert.moeb:
                return str(self.immobilie.ausstattung.moebliert.moeb)

            return True

        return False

    @property
    def seniorengerecht(self):
        """Returns whether the real estate is senior-freindly."""
        try:
            return bool(self.immobilie.ausstattung.seniorengerecht)
        except AttributeError:
            return False

    @property
    def baujahr(self):
        """Returns the year of construction."""
        try:
            baujahr = self.immobilie.zustand_angaben.baujahr
        except AttributeError:
            return None
        else:
            return str(baujahr) if baujahr else None

    @property
    def zustand(self):
        """Returns the condition of the real estate."""
        try:
            zustand = self.immobilie.zustand_angaben.zustand.zustand_art
        except AttributeError:
            return None
        else:
            return str(zustand) if zustand else None

    @property
    def epart(self):
        """Returns the energy certificate type."""
        try:
            epart = self.immobilie.zustand_angaben.energiepass.epart
        except AttributeError:
            return None
        else:
            return str(epart) if epart else None

    @property
    def energieverbrauchkennwert(self):
        """Returns the energy consumption characteristic value."""
        try:
            energieverbrauchkennwert = (
                self.immobilie.zustand_angaben.energiepass
                .energieverbrauchkennwert)
        except AttributeError:
            return None
        else:
            if energieverbrauchkennwert:
                return str(energieverbrauchkennwert)

    @property
    def endenergiebedarf(self):
        """Returns the energy consumption value."""
        try:
            endenergiebedarf = (
                self.immobilie.zustand_angaben.energiepass.endenergiebedarf)
        except AttributeError:
            return None
        else:
            return str(endenergiebedarf) if endenergiebedarf else None

    @property
    def primaerenergietraeger(self):
        """Returns the energy certificate type."""
        try:
            primaerenergietraeger = (
                self.immobilie.zustand_angaben.energiepass
                .primaerenergietraeger)
        except AttributeError:
            return None
        else:
            if primaerenergietraeger:
                return str(primaerenergietraeger)

    @property
    def stromwert(self):
        """Returns the electricity value."""
        try:
            stromwert = self.immobilie.zustand_angaben.energiepass.stromwert
        except AttributeError:
            return None
        else:
            return str(stromwert) if stromwert else None

    @property
    def waermewert(self):
        """Returns the heating value."""
        try:
            waermewert = self.immobilie.zustand_angaben.energiepass.waermewert
        except AttributeError:
            return None
        else:
            return str(waermewert) if waermewert else None

    @property
    def wertklasse(self):
        """Returns the value class."""
        try:
            wertklasse = self.immobilie.zustand_angaben.energiepass.wertklasse
        except AttributeError:
            return None
        else:
            return str(wertklasse) if wertklasse else None

    @property
    def min_mietdauer(self):
        """Minimum rental time."""
        try:
            min_mietdauer = self.immobilie.verwaltung_objekt.min_mietdauer
        except AttributeError:
            return None
        else:
            if min_mietdauer:
                if min_mietdauer.min_dauer:
                    return '{0} {0.min_dauer}'.format(min_mietdauer)

                return str(min_mietdauer)

    @property
    def max_mietdauer(self):
        """Maximum rental time."""
        try:
            max_mietdauer = self.immobilie.verwaltung_objekt.max_mietdauer
        except AttributeError:
            return None
        else:
            if max_mietdauer:
                if max_mietdauer.max_dauer:
                    return '{0} {0.max_dauer}'.format(max_mietdauer)

                return str(max_mietdauer)

    @property
    def laufzeit(self):
        """Remaining time of emphyteusis."""
        try:
            laufzeit = self.immobilie.verwaltung_objekt.laufzeit
        except AttributeError:
            return None
        else:
            return float(laufzeit) if laufzeit else None

    @property
    def max_personen(self):
        """Maximum amount of persons."""
        try:
            max_personen = self.immobilie.verwaltung_objekt.max_personen
        except AttributeError:
            return None
        else:
            return int(max_personen) if max_personen else None

    @property
    def weitergabe_positiv(self):
        """Yields portals to which the real estate may be sent."""
        return self.immobilie.weitergabe_positiv

    @property
    def weitergabe_negativ(self):
        """Yields portals to which the real estate may NOT be sent."""
        return self.immobilie.weitergabe_negativ

    @property
    def weitergabe_generell(self):
        """Determines general redirection restrictions."""
        return self.immobilie.weitergabe_generell

    @property
    def active(self):
        """Determines whether the real estate is active."""
        return 'true' if self.immobilie.active else 'false'

    def evaluate(self, operation):
        """Real estate evaluation callback."""
        option = None
        operator = None
        raw_value = None

        for operator in OPERATIONS:
            try:
                option, raw_value = operation.split(operator)
            except ValueError:
                continue
            else:
                # Compensate for ">", "<", "=>" and "<="
                if option in ('>', '<'):
                    if raw_value.startswith('='):
                        option += '='
                        raw_value = raw_value[1:]
                    # Compensate for legacy ">>" → ">" and "<<" → "<"
                    elif raw_value.startswith(option):
                        raw_value = raw_value[1:]

                break

        if option is None or raw_value is None:
            raise InvalidFilterOption(operation)

        operation_func = OPERATIONS.get(operator)

        if operation_func is None:
            raise FilterOperationNotImplemented(operator)

        try:
            option_ = OPTIONS[option]
        except KeyError:
            raise InvalidFilterOption(option)
        else:
            try:
                option_format, option_func = option_
            except TypeError:
                option_format = None
                option_func = option_

            try:
                value = cast(raw_value, typ=option_format)
            except DontCare as dont_care:
                return bool(dont_care)
            else:
                try:
                    val = option_func(self)
                    result = operation_func(val, value)
                except (TypeError, ValueError):
                    # Exclude for None values and wrong types
                    return False
                except AttributeError:
                    raise SievingError(option, operator, raw_value)
                else:
                    return bool(result)


class RealEstateSieve:
    """Class that sieves real estates by certain filters."""

    def __init__(self, real_estates, filters):
        """Sets the respective realtor and filter tuples like:
        (<option>, <operation>, <target_value>).
        """
        self.real_estates = real_estates
        self.filters = filters

    def __iter__(self):
        """Sieve real estates by the given filters."""
        if self.filters:
            for orm, dom in self.real_estates:
                filterable_real_estate = FilterableRealEstate(dom)
                applicable = evaluate(
                    self.filters, callback=filterable_real_estate.evaluate)

                try:
                    if applicable:
                        yield (orm, dom)
                    else:
                        print('Filtered real estate: {}.'.format(
                            dom.objektnr_extern), flush=True)
                except SecurityError as sec_err:
                    raise SecurityBreach(str(sec_err)) from None
        else:
            for real_estate in self.real_estates:
                yield real_estate
