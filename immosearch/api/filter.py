"""Real estate filtering"""

from .lib import Delims, Operators

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['Filterable']


operations = {Operators.EQ: lambda x, y: x == y,
              # Operators.EG: ,
              Operators.EC: lambda x, y: x.lower() == y.lower(),
              Operators.NE: lambda x, y: x != y,
              # Operators.NG: ,
              Operators.NC: lambda x, y: x.lower() != y.lower(),
              Operators.LT: lambda x, y: x < y,
              Operators.NE: lambda x, y: x <= y,
              Operators.GT: lambda x, y: x > y,
              Operators.GE: lambda x, y: x >= y,
              Operators.IN: lambda x, y: x in y,
              Operators.NI: lambda x, y: x not in y}


options = {'objektart': lambda f, op, v: op(f.object_types, v),
           'land': lambda f, op, v: op(f.country, v),
           'stadt': lambda f, op, v: op(f.city, v)}


def parse(val, typ=None):
    """Parse a raw string value for a certain type
    XXX: Nested lists are not supported, yet
    """
    if typ is None:  # Cast intelligent
        # Check for list
        if val.startswith(Delims.SL) and val.endswith(Delims.EL):
            return [parse(elem.strip()) for elem in val[1:-1].split(Delims.IS)]
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
                    lower_val = val.lower()
                    if lower_val == 'true':
                        return True
                    elif lower_val == 'false':
                        return False
                    # Return raw string if nothing else fits
                    else:
                        return val
                else:
                    return f
            else:
                return i
    else:
        return typ(val)  # Cast with specified constructor method


class Filterable():
    """Wrapper class for an OpenImmo™-Immobilie
    that can be filtered by certain attributes
    """

    def __init__(self, immobilie):
        """Sets the appropriate OpenImmo™-immobilie"""
        self.__immobilie = immobilie

    @classmethod
    def fromanbieter(cls, anbieter):
        """Yields filterable real estates from a realtor"""
        for immobilie in anbieter.immobilie:
            yield cls(immobilie)

    @property
    def immobilie(self):
        """Returns the appropriate immobilie"""
        return self.__immobilie

    @immobilie.setter
    def _immobilie(self, immobilie):
        """Sets the appropriate immobilie"""
        self.__immobilie = immobilie

    @property
    def object_types(self):
        """Returns a generator for the object's types"""
        oa = self.immobilie.objektkategorie.objektart
        for zimmer in oa.zimmer:
            yield str(zimmer.zimmertyp) if zimmer.zimmertyp else 'ZIMMER'
        for wohnung in oa.wohnung:
            yield str(wohnung.wohnungtyp) if wohnung.wohnungtyp else 'WOHNUNG'
        for haus in oa.haus:
            yield str(haus.haustyp) if haus.haustyp else 'HAUS'
        for grundstueck in oa.grundstueck:
            if grundstueck.grundst_typ:
                yield str(grundstueck.grundst_typ)
            else:
                yield 'GRUNDSTUECK'
        for buero_praxen in oa.buero_praxen:
            if buero_praxen.buero_typ:
                yield str(buero_praxen.buero_typ)
            else:
                yield 'BUERO_PRAXEN'
        for einzelhandel in oa.einzelhandel:
            if einzelhandel.handel_typ:
                yield str(einzelhandel.handel_typ)
            else:
                yield 'EINZELHANDEL'
        for gastgewerbe in oa.gastgewerbe:
            if gastgewerbe.gastgew_typ:
                str(gastgewerbe.gastgew_typ)
            else:
                yield 'GASTGEWERBE'
        for hallen_lager_prod in oa.hallen_lager_prod:
            if hallen_lager_prod.hallen_typ:
                yield str(hallen_lager_prod.hallen_typ)
            else:
                yield 'HALLEN_LAGER_PROD'
        for land_und_forstwirtschaft in oa.land_und_forstwirtschaft:
            if land_und_forstwirtschaft.land_typ:
                yield str(land_und_forstwirtschaft.land_typ)
            else:
                yield 'LAND_UND_FORSTWIRTSCHAFT'
        for parken in oa.parken:
            yield str(parken.parken_typ) if parken.parken_typ else 'PARKEN'
        for sonstige in oa.sonstige:
            if sonstige.sonstige_typ:
                yield str(sonstige.sonstige_typ)
            else:
                yield 'SONSTIGE'
        for freizeitimmobilie_gewerblich in oa.freizeitimmobilie_gewerblich:
            if freizeitimmobilie_gewerblich.freizeit_typ:
                yield str(freizeitimmobilie_gewerblich.freizeit_typ)
            else:
                yield 'FREIZEITIMMOBILIE_GEWERBLICH'
        for zinshaus_renditeobjekt in oa.zinshaus_renditeobjekt:
            if zinshaus_renditeobjekt.zins_typ:
                yield str(zinshaus_renditeobjekt.zins_typ)
            else:
                yield 'ZINSHAUS_RENDITEOBJEKT'

    @property
    def country(self):
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
    def city(self):
        """Returns the city"""
        if self.immobilie.geo.ort is not None:
            return str(self.immobilie.geo.ort)
        else:
            return None

    @property
    def district(self):
        """Returns the city's district"""
        if self.immobilie.geo.regionaler_zusatz is not None:
            return str(self.immobilie.geo.regionaler_zusatz)
        else:
            return None

    @property
    def zip(self):
        """Returns the ZIP code"""
        if self.immobilie.geo.plz is not None:
            return str(self.immobilie.geo.plz)
        else:
            return None

    @property
    def street(self):
        """Returns the ZIP code"""
        if self.immobilie.geo.strasse is not None:
            return str(self.immobilie.geo.strasse)
        else:
            return None

    @property
    def house_number(self):
        """Returns the house number"""
        if self.immobilie.geo.hausnummer is not None:
            return str(self.immobilie.geo.hausnummer)
        else:
            return None

    @property
    def rooms(self):
        """Returns the number of rooms"""
        if self.immobilie.flaechen.anzahl_zimmer is not None:
            return float(self.immobilie.flaechen.anzahl_zimmer)
        else:
            return None

    @property
    def floor(self):
        """Returns the floor of the flat / room"""
        if self.immobilie.geo.etage is not None:
            return int(self.immobilie.geo.etage)
        else:
            return None

    @property
    def floors(self):
        """Returns the number of floors of the building"""
        if self.immobilie.geo.anzahl_etagen is not None:
            return int(self.immobilie.geo.anzahl_etagen)
        else:
            return None

    @property
    def living_space(self):
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
    def property_area(self):
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
    def balconies(self):
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
    def terraces(self):
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
    def cold_rent(self):
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
    def warm_rent(self):
        """Returns the price of the warm rent"""
        try:
            warmmiete = self.immobilie.preise.warmmiete
        except AttributeError:
            return None
        else:
            if warmmiete is not None:
                return float(warmmiete)
            else:
                return None

    @property
    def ancillary_expenses(self):
        """Returns the price of the ancillary expenses"""
        try:
            nebenkosten = self.immobilie.preise.nebenkosten
        except AttributeError:
            return None
        else:
            if nebenkosten is not None:
                return float(nebenkosten)
            else:
                return None

    @property
    def purchase_price(self):
        """Returns the purchase price"""
        try:
            kaufpreis = self.immobilie.preise.kaufpreis
        except AttributeError:
            return None
        else:
            if kaufpreis is not None:
                return float(kaufpreis)
            else:
                return None
