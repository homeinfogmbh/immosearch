"""Real estate data filtering"""

from openimmo import openimmo

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['Selections', 'RealEstateSelector']


# Available picture types
PIC_TYPES = ['image/jpeg', 'image/png', 'image/gif']

# User defined simple field for attachment counts
HI_ATT_CNT = 'homeinfo_attachment_count'


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


class RealEstateSelector():
    """Class that filters real estates of a user"""

    def __init__(self, real_estates, selections, attachment_limit,
                 count_attachments):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        self._real_estates = real_estates
        self._selections = selections
        self._attachment_limit = attachment_limit
        self._count_attachments = count_attachments

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def selections(self):
        """Returns the selections"""
        return self._selections

    @property
    def attachment_limit(self):
        """Returns the attachment limit"""
        return self._attachment_limit

    @property
    def count_attachments(self):
        """Returns the amount of available attachments"""
        return self._count_attachments

    @property
    def immobilie(self):
        """Returns real estates liited to the selections"""
        for real_estate in self.real_estates:
            # Count pictures if requested
            if self.count_attachments:
                if real_estate.anhaenge:
                    picc = len([a for a in real_estate.anhaenge.anhang
                                if a.mimetype in PIC_TYPES])
                else:
                    picc = 0
                udx = openimmo.user_defined_extend()
                feld = openimmo.CTD_ANON_67()
                feld.name = HI_ATT_CNT
                feld.wert = str(picc)
                udx.feld = feld
                real_estate.user_defined_extend.append(udx)
            # Make selections
            if Selections.FREITEXTE not in self.selections:
                real_estate.freitexte = None
            if Selections.ATATCHMENTS not in self.selections:
                real_estate.anhaenge = None
            if self.attachment_limit is not None:
                if real_estate.anhaenge:
                    limited_atts = []
                    for c, att in enumerate(real_estate.anhaenge.anhang):
                        if c < self.attachment_limit:
                            limited_atts.append(att)
                        else:
                            break
                    real_estate.anhaenge.anhang = limited_atts
            yield real_estate
