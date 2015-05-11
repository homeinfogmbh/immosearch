"""Real estate data filtering"""

from openimmo import openimmo
from openimmo.openimmo import AttachmentError
from contextlib import suppress

__all__ = ['Selections', 'RealEstateSelector']

# Available picture types
PIC_TYPES = ['image/jpeg', 'image/png', 'image/gif']

# User defined simple field for attachment counts
HI_PIC_CNT = 'homeinfo_picc'


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    ATATCHMENTS = 'attachments'


class RealEstateSelector():
    """Class that filters real estates of a user"""

    def __init__(self, immobilie, selections=None, attachment_limit=None,
                 attachment_index=None, attachment_title=None,
                 attachment_group=None, count_pictures=False):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        self._immobilie = immobilie
        self._selections = selections
        self._attachment_limit = attachment_limit
        self._attachment_index = attachment_index
        self._attachment_title = attachment_title
        self._attachment_group = attachment_group
        self._count_pictures = count_pictures

    @property
    def immobilie(self):
        """Returns the real estates"""
        return self._immobilie

    @property
    def selections(self):
        """Returns the selections"""
        return self._selections

    @property
    def attachment_limit(self):
        """Returns the attachment limit"""
        return self._attachment_limit

    @property
    def attachment_index(self):
        """Returns the attachment index"""
        return self._attachment_index

    @property
    def attachment_title(self):
        """Returns the attachment title"""
        return self._attachment_title

    @property
    def attachment_group(self):
        """Returns the attachment group"""
        return self._attachment_group

    @property
    def count_pictures(self):
        """Returns the amount of available pictures"""
        return self._count_pictures

    def __iter__(self):
        """Returns real estates liited to the selections"""
        for immobilie in self.immobilie:
            # Count pictures if requested
            if self.count_pictures:
                if immobilie.anhaenge:
                    for n, _ in enumerate(a for a in
                                          immobilie.anhaenge.anhang
                                          if a.mimetype in PIC_TYPES):
                        pass
                    try:
                        picc = n + 1
                    except NameError:
                        picc = 0
                else:
                    picc = 0
                udx = openimmo.user_defined_extend()
                feld = openimmo.CTD_ANON_67()
                feld.name = HI_PIC_CNT
                feld.wert = str(picc)
                udx.feld.append(feld)
                immobilie.user_defined_extend.append(udx)
            # Discard freitexte iff not selected
            if Selections.FREITEXTE not in self.selections:
                immobilie.freitexte = None
            # Discard attachments iff not selected
            if Selections.ATATCHMENTS not in self.selections:
                immobilie.anhaenge = None
            # Select indexes iff specified
            if self.attachment_index is not None:
                if immobilie.anhaenge:
                    limited_atts = []
                    for c, att in enumerate(immobilie.anhaenge.anhang):
                        if c == self.attachment_index:
                            limited_atts.append(att)
                            break
                    immobilie.anhaenge.anhang = limited_atts
            # Select titles iff specified
            if self.attachment_title is not None:
                if immobilie.anhaenge:
                    limited_atts = []
                    for att in immobilie.anhaenge.anhang:
                        if att.anhangtitel == self.attachment_title:
                            limited_atts.append(att)
                    immobilie.anhaenge.anhang = limited_atts
            # Select attachments by group
            if self.attachment_group is not None:
                if immobilie.anhaenge:
                    limited_atts = []
                    for att in immobilie.anhaenge.anhang:
                        if att.gruppe == self.attachment_group:
                            limited_atts.append(att)
                    immobilie.anhaenge.anhang = limited_atts
            # Limit attachments if limit is specified
            if self.attachment_limit is not None:
                if immobilie.anhaenge:
                    limited_atts = []
                    for c, att in enumerate(immobilie.anhaenge.anhang):
                        if c < self.attachment_limit:
                            with suppress(AttachmentError):
                                limited_atts.append(att.insource())
                        else:
                            break
                    immobilie.anhaenge.anhang = limited_atts
            else:   # Just insource all attachments
                if immobilie.anhaenge:
                    for att in immobilie.anhaenge.anhang:
                        with suppress(AttachmentError):
                            limited_atts.append(att.insource())
                    immobilie.anhaenge.anhang = limited_atts
            yield immobilie
