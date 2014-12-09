"""
Real estate filtering
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['FilterOptions', 'FilterableRealEstate']


class FilterMethods():
    """
    Methods for filtering
    """
    EQ = '=='
    NEQ = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    IN = '∈'
    AND = '+'


class FilterOptions():
    """
    Options for filtering
    """
    OBJEKTART = 'OBJEKTART'
    LAND = 'LAND'
    STADT = 'STADT'
    ORT = 'ORT'
    PLZ = 'PLZ'
    STRASSE = 'STRASSE'
    HAUSNUMMER = 'HAUSNUMMER'
    ZIMMER = 'ZIMMER'   # Number of rooms
    ETAGE = 'ETAGE'     # The flat's / room's floor
    ETAGEN = 'ETAGEN'   # The building's amount of floors
    WOHNFLAECHE = 'WOHNFLAECHE'
    GRUNDSTUECKSFLAECHE = 'GRUNDSTUECKSFLAECHE'
    BALKON = 'BALKON'
    TERRASSE = 'TERRASSE'
    KALTMIETE = 'KALTMIETE'
    WARMMIETE = 'WARMMIETE'
    NEBENKOSTEN = 'NEBENKOSTEN'
    KAUFPREIS = 'KAUFPREIS'


class FilterableRealEstate():
    """
    Wrapper class for an OpenImmo™-Immobilie
    that can be filtered by certain attributes
    """
    def __init__(self, immobilie):
        """Sets the appropriate OpenImmo™-immobilie"""
        self.__immobilie = immobilie

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
