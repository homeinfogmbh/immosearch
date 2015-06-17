"""General API library"""

from datetime import datetime

__all__ = ['boolean', 'debug', 'pdate', 'tags', 'cast', 'Sorting', 'Delims',
           'Operators', 'Realtor', 'RealEstateWrapper']


boolean = {'true': True,
           'false': False}


def debug(s, d=None):
    """Write debug data"""
    msg = ''.join([str(datetime.now()), '\t',
                   str(s) if d is None else '\t'.join([d, str(s)]), '\n'])
    with open('/tmp/auth.txt', 'a') as f:
        f.write(msg)


def pdate(date_str):
    """Parse a datetime string"""
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')


def tags(template, tag_open='<%', tag_close='%>'):
    """Yields tags found in a template"""
    record = False
    window = ''
    token = tag_open
    tag = ''
    for c in template:
        # Records tag content iff in record mode
        if record:
            tag += c
        # Increase window size
        if len(window) < len(token):
            window += c
        else:   # Move window
            window = window[1:len(token)] + c
        # Check for opening tag
        if not record and window == tag_open:
            # Reset window, record and token
            record = True
            window = ''
            token = tag_close
        # Check for closing tag
        elif record and window == tag_close:
            # Remove current window from end of tag
            tag_content = tag[:-len(window)]
            # Reset window, record, token and tag
            window = ''
            record = False
            token = tag_open
            tag = ''
            yield tag_content


def cast(val, typ=None):
    """Type cast a raw string value for a certain type
    XXX: Nested lists are not supported, yet
    """
    if typ is None:  # Cast intelligent
        # Check for list
        if val.startswith(Delims.SL) and val.endswith(Delims.EL):
            return [cast(elem.strip()) for elem in val[1:-1].split(Delims.IS)]
        else:
            # Check for integer
            try:
                i = int(val)
            except ValueError:
                # Check for float
                try:
                    f = float(val)
                except ValueError:
                    # Check for boolean
                    b = boolean.get(val.lower())
                    if b is not None:
                        return b
                    else:
                        # Try to parse a date string
                        try:
                            d = pdate(val)
                        # Return raw string if nothing else fits
                        except ValueError:
                            return val
                        else:
                            return d
                else:
                    return f
            else:
                return i
    else:
        return typ(val)  # Cast with specified constructor method


class Sorting():
    """Sorting types"""

    ASC = 'ASC'
    DESC = 'DESC'


class Delims():
    """Delimiters"""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ';'    # Item separator
    BEGIN_INDEX = '['
    END_INDEX = ']'


class Operators():
    """Filtering operators"""

    EQ = '=='   # Equals
    EG = '~='   # Equals glob
    EC = '%='   # Equals case-insensitive
    NE = '!='   # Does not equal
    NG = '!~'   # Does not glob
    NC = '!%'   # Does not equal case-insensitive
    LT = '<<'   # Less-than
    LE = '<='   # Less-than or equal
    GT = '>>'   # Greater-than
    GE = '>='   # Greater-than or equal
    IN = '∈'    # Element in iterable
    NI = '∉'    # Element not in iterable
    CO = '∋'    # List contains element
    CN = '∌'    # List does not contain element

    def __iter__(self):
        """Iterates over the operators"""
        for attr in dir(self):
            if (attr.upper() == attr) and (len(attr) == 2):
                yield getattr(self, attr)


class Realtor():
    """Wrapper class for an OpenImmo™-anbieter
    that can be filtered by certain attributes
    """

    def __init__(self, anbieter):
        """Sets the appropriate OpenImmo™-anbieter"""
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


class RealEstateWrapper():
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
        """Returns the OpenImmo™-Objektart
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
                yield str(gastgewerbe.gastgew_typ)
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
        """Amount of balconies"""
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
            return float(kaltmiete) if kaltmiete else None

    @property
    def nettokaltmiete(self):
        """Returns the net value of the cold rent"""
        try:
            nettokaltmiete = self.immobilie.preise.nettokaltmiete
        except AttributeError:
            return None
        else:
            return float(nettokaltmiete) if nettokaltmiete else None

    @property
    def _gesamtmiete(self):
        """Returns the total rent"""
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
        return result

    @property
    def warmmiete(self):
        """Returns the price of the warm rent"""
        try:
            warmmiete = self.immobilie.preise.warmmiete
        except AttributeError:
            return self._gesamtmiete
        else:
            return float(warmmiete) if warmmiete else self._gesamtmiete

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
    def heizkosten(self):
        """Returns the heating costs"""
        try:
            heizkosten = self.immobilie.preise.heizkosten
        except AttributeError:
            return None
        else:
            return float(heizkosten) if heizkosten else None

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
