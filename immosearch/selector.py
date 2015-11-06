"""Real estate data selecting"""
from openimmodb3.db import Attachment
from peewee import DoesNotExist
from openimmo import openimmo

__all__ = ['Selections', 'RealEstateDataSelector']


class Selections():
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    TITLEPIC = 'titlepic'
    ALLATTS = 'allatts'  # All attachments


class RealEstateDataSelector():
    """Class that filters real estates of a user"""

    def __init__(self, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        self._real_estates = real_estates
        self._selections = selections or []

    @property
    def real_estates(self):
        """Returns the real estates"""
        return self._real_estates

    @property
    def selections(self):
        """Returns the selections"""
        return self._selections

    def __iter__(self):
        """Returns real estates limited to the selections"""
        freitexte = Selections.FREITEXTE in self.selections
        titlepic = Selections.TITLEPIC in self.selections
        allatts = Selections.ALLATTS in self.selections
        for real_estate in self.real_estates:
            # Discard freitexte iff not selected
            if not freitexte:
                real_estate.dom.freitexte = None
            if allatts:
                if real_estate.dom.anhaenge is None:
                    real_estate.dom.anhaenge = openimmo.anhaenge()
                for attachment in Attachment.select().where(
                        Attachment.immobilie == real_estate.orm):
                    real_estate.dom.anhaenge.anhang.append(attachment.dom)
            elif titlepic:
                try:
                    title_picture = Attachment.get(
                        (Attachment.immobilie == real_estate.orm) &
                        (Attachment.group == 'TITELBILD'))
                except DoesNotExist:
                    try:
                        title_picture = Attachment.get(
                            (Attachment.immobilie == real_estate.orm) &
                            (Attachment.group == 'AUSSENANSICHTEN'))
                    except DoesNotExist:
                        try:
                            title_picture = Attachment.get(
                                (Attachment.immobilie == real_estate.orm) &
                                (Attachment.group == 'INNENANSICHTEN'))
                        except DoesNotExist:
                            try:
                                title_picture = Attachment.get(
                                    Attachment.immobilie == real_estate.orm)
                            except DoesNotExist:
                                title_picture = None
                if title_picture is not None:
                    anhaenge = openimmo.anhaenge()
                    anhaenge.anhang.append(title_picture.dom)
                    real_estate.dom.anhaenge = anhaenge
            # Iff object description is missing,
            # replace it with the three-liner
            if real_estate.dom.freitexte:
                if not real_estate.dom.freitexte.objektbeschreibung:
                    real_estate.dom.freitexte.objektbeschreibung = \
                        real_estate.dom.freitexte.dreizeiler
            yield real_estate
