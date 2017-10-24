"""Real estate data selecting."""
from enum import Enum

from peewee import DoesNotExist

from openimmo import openimmo
from openimmodb import Immobilie, Anhang

from .errors import InvalidAttachmentLimit

__all__ = ['Selections', 'RealEstateDataSelector']


BASE_URL = 'https://backend.homeinfo.de/immosearch/attachment/{}'


def to_orm(real_estate_dom, customer):
    """Gets the ORM model for the respective real estate."""

    return Immobilie.get(
        (Immobilie.customer == customer) &
        (Immobilie.objektnr_extern == real_estate_dom.objektnr_extern))


def set_all_attachments(orm_id, real_estate):
    """Sets all attachments to the real estate."""

    for attachment in Anhang.by_immobilie(orm_id):
        real_estate.anhaenge.anhang.append(attachment.remote(BASE_URL))


def set_attachments(orm_id, real_estate, attachments):
    """Sets desired amount of attachments."""

    for number, attachment in enumerate(Anhang.by_immobilie(orm_id)):
        if number >= attachments:
            break

        real_estate.anhaenge.anhang.append(attachment.remote(BASE_URL))


def set_titlepic(orm_id, real_estate):
    """Sets the title picture."""

    try:
        title_picture = Anhang.get(
            (Anhang.immobilie == orm_id)
            & (Anhang.gruppe == 'TITELBILD'))
    except DoesNotExist:
        try:
            title_picture = Anhang.get(
                (Anhang.immobilie == orm_id)
                & (Anhang.gruppe == 'AUSSENANSICHTEN'))
        except DoesNotExist:
            try:
                title_picture = Anhang.get(
                    (Anhang.immobilie == orm_id)
                    & (Anhang.gruppe == 'INNENANSICHTEN'))
            except DoesNotExist:
                try:
                    title_picture = Anhang.get(Anhang.immobilie == orm_id)
                except DoesNotExist:
                    title_picture = None

    if title_picture is not None:
        real_estate.anhaenge.anhang.append(title_picture.remote(BASE_URL))


def set_free_texts(real_estate, freitexte):
    """Sets free texts on the real estate."""

    if not freitexte:
        real_estate.freitexte = None
    else:
        # Iff object description is missing,
        # replace it with the three-liner.
        if real_estate.freitexte:
            if not real_estate.freitexte.objektbeschreibung:
                real_estate.freitexte.objektbeschreibung = \
                    real_estate.freitexte.dreizeiler


class Selections(Enum):
    """Specifies sleection options."""

    FREITEXTE = 'freitexte'
    TITLEPIC = 'titlepic'
    N_ATTS = 'atts'  # Some attachments
    ALLATTS = 'allatts'  # All attachments


class RealEstateDataSelector:
    """Class that filters real estates of a user."""

    def __init__(self, customer, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit.
        """
        self.customer = customer
        self.real_estates = real_estates
        self.selections = selections or []

    def __iter__(self):
        """Returns real estates limited to the selections."""
        for real_estate in self.real_estates:
            if real_estate.anhaenge is None:
                real_estate.anhaenge = openimmo.anhaenge()

            orm_id = to_orm(real_estate, self.customer)
            attachments = self.attachments

            if self.allatts:
                set_all_attachments(orm_id, real_estate)
            elif attachments is not None:
                set_attachments(orm_id, real_estate, attachments)
            elif self.titlepic:
                set_titlepic(orm_id, real_estate)

            set_free_texts(real_estate, self.freitexte)
            print('Processed real estate: {}.'.format(
                real_estate.objektnr_extern), flush=True)
            yield real_estate

    @property
    def freitexte(self):
        """Determines whether free texts are wanted."""
        return Selections.FREITEXTE.value in self.selections

    @property
    def titlepic(self):
        """Determines whether the title image is wanted."""
        return Selections.TITLEPIC.value in self.selections

    @property
    def allatts(self):
        """Determines whether all attachments are wanted."""
        return Selections.ALLATTS.value in self.selections

    @property
    def attachments(self):
        """Returns the amount of wanted attachments."""
        for selection in self.selections:
            if selection.endswith(Selections.N_ATTS.value):
                try:
                    number, _ = selection.split(Selections.N_ATTS.value)
                except ValueError:
                    raise InvalidAttachmentLimit(number)
                else:
                    try:
                        return int(number)
                    except ValueError:
                        raise InvalidAttachmentLimit(number)
