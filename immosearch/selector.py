"""Real estate data selecting"""

from peewee import DoesNotExist

from homeinfo.misc import Enumeration
from openimmo import openimmo
from openimmodb import Anhang

from .errors import InvalidAttachmentLimit

__all__ = ['Selections', 'RealEstateDataSelector']


class Selections(Enumeration):
    """Specifies sleection options"""

    FREITEXTE = 'freitexte'
    TITLEPIC = 'titlepic'
    N_ATTS = 'atts'  # Some attachments
    ALLATTS = 'allatts'  # All attachments


class RealEstateDataSelector():
    """Class that filters real estates of a user"""

    BASE_URL = 'https://backend.homeinfo.de/immosearch/attachment/{}'

    def __init__(self, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit
        """
        self.real_estates = real_estates
        self.selections = selections or []

    def __iter__(self):
        """Returns real estates limited to the selections"""
        freitexte = Selections.FREITEXTE in self.selections
        titlepic = Selections.TITLEPIC in self.selections
        allatts = Selections.ALLATTS in self.selections
        attachments = None

        if not allatts:
            for selection in self.selections:
                if selection.endswith(Selections.N_ATTS):
                    n, _ = selection.split(Selections.N_ATTS)

                    try:
                        attachments = int(n)
                    except ValueError:
                        raise InvalidAttachmentLimit(n)

        for real_estate in self.real_estates:
            # Discard freitexte iff not selected
            if not freitexte:
                real_estate.dom.freitexte = None

            if allatts:
                if real_estate.dom.anhaenge is None:
                    real_estate.dom.anhaenge = openimmo.anhaenge()

                for attachment in Anhang.by_immobilie(real_estate.orm):
                    real_estate.dom.anhaenge.anhang.append(
                        attachment.remote(self.BASE_URL))
            elif attachments is not None:
                if real_estate.dom.anhaenge is None:
                    real_estate.dom.anhaenge = openimmo.anhaenge()

                for n, attachment in enumerate(Anhang.by_immobilie(
                        real_estate.orm)):
                    if n >= attachments:
                        break
                    else:
                        real_estate.dom.anhaenge.anhang.append(
                            attachment.remote(self.BASE_URL))
            elif titlepic:
                try:
                    title_picture = Anhang.get(
                        (Anhang.immobilie == real_estate.orm) &
                        (Anhang.gruppe == 'TITELBILD'))
                except DoesNotExist:
                    try:
                        title_picture = Anhang.get(
                            (Anhang.immobilie == real_estate.orm) &
                            (Anhang.gruppe == 'AUSSENANSICHTEN'))
                    except DoesNotExist:
                        try:
                            title_picture = Anhang.get(
                                (Anhang.immobilie == real_estate.orm) &
                                (Anhang.gruppe == 'INNENANSICHTEN'))
                        except DoesNotExist:
                            try:
                                title_picture = Anhang.get(
                                    Anhang.immobilie == real_estate.orm)
                            except DoesNotExist:
                                title_picture = None

                if title_picture is not None:
                    anhaenge = openimmo.anhaenge()
                    anhaenge.anhang.append(title_picture.remote(self.BASE_URL))
                    real_estate.dom.anhaenge = anhaenge

            # Iff object description is missing,
            # replace it with the three-liner
            if real_estate.dom.freitexte:
                if not real_estate.dom.freitexte.objektbeschreibung:
                    real_estate.dom.freitexte.objektbeschreibung = \
                        real_estate.dom.freitexte.dreizeiler

            yield real_estate
