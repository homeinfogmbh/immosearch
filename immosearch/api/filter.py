"""
Real estate filtering
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['FilterOptions', 'FilterableRealEstate']


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
        """Returns a generator of the object's types"""
        oa = self.immobilie.objektkategorie.objektart
        for zimmer in oa.zimmer:
            yield str(zimmer.zimmertyp) if zimmer.zimmertyp else 'ZIMMER'
        for wohnung in oa.wohnung:
            yield str(wohnung.wohnungtyp) if wohnung.wohnungtyp else 'WOHNUNG'
        for haus in oa.haus:
            yield str(haus.haustyp) if haus.haustyp else 'HAUS'
        for grundstueck in oa.grundstueck:
            yield (str(grundstueck.grundst_typ)
                   if grundstueck.grundst_typ
                   else 'GRUNDSTUECK')
        for buero_praxen in oa.buero_praxen:
            yield (str(buero_praxen.buero_typ)
                   if buero_praxen.buero_typ
                   else 'BUERO_PRAXEN')
        for einzelhandel in oa.einzelhandel:
            yield (str(einzelhandel.handel_typ)
                   if einzelhandel.handel_typ
                   else 'EINZELHANDEL')
        for gastgewerbe in oa.gastgewerbe:
            yield (str(gastgewerbe.gastgew_typ)
                   if gastgewerbe.gastgew_typ
                   else 'GASTGEWERBE')
        for hallen_lager_prod in oa.hallen_lager_prod:
            yield (str(hallen_lager_prod.hallen_typ)
                   if hallen_lager_prod.hallen_typ
                   else 'HALLEN_LAGER_PROD')
        for land_und_forstwirtschaft in oa.land_und_forstwirtschaft:
            yield (str(land_und_forstwirtschaft.land_typ)
                   if land_und_forstwirtschaft.land_typ
                   else 'LAND_UND_FORSTWIRTSCHAFT')
        for parken in oa.parken:
            yield str(parken.parken_typ) if parken.parken_typ else 'PARKEN'
        for sonstige in oa.sonstige:
            yield (str(sonstige.sonstige_typ)
                   if sonstige.sonstige_typ
                   else 'SONSTIGE')
        for freizeitimmobilie_gewerblich in oa.freizeitimmobilie_gewerblich:
            yield (str(freizeitimmobilie_gewerblich.freizeit_typ)
                   if freizeitimmobilie_gewerblich.freizeit_typ
                   else 'FREIZEITIMMOBILIE_GEWERBLICH')
        for zinshaus_renditeobjekt in oa.zinshaus_renditeobjekt:
            yield (str(zinshaus_renditeobjekt.zins_typ)
                   if zinshaus_renditeobjekt.zins_typ
                   else 'ZINSHAUS_RENDITEOBJEKT')

    @property
    def country(self):
        """Returns the country"""
        try:
            if self.immobilie.geo.land.iso_land is not None:
                return str(self.immobilie.geo.land.iso_land)
            else:
                return None
        except:
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
