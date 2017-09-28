"""Real estate data selecting."""
from enum import Enum

from peewee import DoesNotExist

from openimmo import openimmo
from openimmodb import Immobilie, Anhang

from .errors import InvalidAttachmentLimit

__all__ = ['Selections', 'RealEstateDataSelector']


def to_orm(real_estate, customer):
    """Gets the ORM model for the respective real estate."""

    return Immobilie.get(
        (Immobilie.customer == customer) &
        (Immobilie.objektnr_extern == real_estate.objektnr_extern))


class Selections(Enum):
    """Specifies sleection options."""

    FREITEXTE = 'freitexte'
    TITLEPIC = 'titlepic'
    N_ATTS = 'atts'  # Some attachments
    ALLATTS = 'allatts'  # All attachments


class RealEstateDataSelector:
    """Class that filters real estates of a user."""

    BASE_URL = 'https://backend.homeinfo.de/immosearch/attachment/{}'

    def __init__(self, customer, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit.
        """
        self.customer = customer
        self.real_estates = real_estates
        self.selections = selections or []

    def __iter__(self):
        """Returns real estates limited to the selections."""
        freitexte = Selections.FREITEXTE.value in self.selections
        titlepic = Selections.TITLEPIC.value in self.selections
        allatts = Selections.ALLATTS.value in self.selections
        attachments = None

        if not allatts:
            for selection in self.selections:
                if selection.endswith(Selections.N_ATTS.value):
                    number, _ = selection.split(Selections.N_ATTS.value)

                    try:
                        attachments = int(number)
                    except ValueError:
                        raise InvalidAttachmentLimit(number)

        for real_estate in self.real_estates:
            orm_id = to_orm(real_estate, self.customer).id
            # Discard freitexte iff not selected
            if not freitexte:
                real_estate.freitexte = None

            if allatts:
                if real_estate.anhaenge is None:
                    real_estate.anhaenge = openimmo.anhaenge()

                for attachment in Anhang.by_immobilie(orm_id):
                    real_estate.anhaenge.anhang.append(
                        attachment.remote(self.BASE_URL))
            elif attachments is not None:
                if real_estate.anhaenge is None:
                    real_estate.anhaenge = openimmo.anhaenge()

                for number, attachment in enumerate(Anhang.by_immobilie(
                        orm_id)):
                    if number >= attachments:
                        break
                    else:
                        real_estate.anhaenge.anhang.append(
                            attachment.remote(self.BASE_URL))
            elif titlepic:
                try:
                    title_picture = Anhang.get(
                        (Anhang.immobilie == orm_id) &
                        (Anhang.gruppe == 'TITELBILD'))
                except DoesNotExist:
                    try:
                        title_picture = Anhang.get(
                            (Anhang.immobilie == orm_id) &
                            (Anhang.gruppe == 'AUSSENANSICHTEN'))
                    except DoesNotExist:
                        try:
                            title_picture = Anhang.get(
                                (Anhang.immobilie == orm_id) &
                                (Anhang.gruppe == 'INNENANSICHTEN'))
                        except DoesNotExist:
                            try:
                                title_picture = Anhang.get(
                                    Anhang.immobilie == orm_id)
                            except DoesNotExist:
                                title_picture = None

                if title_picture is not None:
                    anhaenge = openimmo.anhaenge()
                    anhaenge.anhang.append(title_picture.remote(self.BASE_URL))
                    real_estate.anhaenge = anhaenge

            # Iff object description is missing,
            # replace it with the three-liner
            if real_estate.freitexte:
                if not real_estate.freitexte.objektbeschreibung:
                    real_estate.freitexte.objektbeschreibung = \
                        real_estate.freitexte.dreizeiler

            yield real_estate
