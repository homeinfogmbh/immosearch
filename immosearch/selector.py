"""Real estate data selecting."""

from enum import Enum
from re import compile as compile_

from openimmo import anhaenge
from openimmodb import Anhang

from .errors import InvalidAttachmentLimit


__all__ = ["Selections", "RealEstateDataSelector"]


BASE_URL = "https://backend.homeinfo.de/immosearch/attachment/{}"
TITLEPIC_SEARCH_GROUPS = ("TITELBILD", "AUSSENANSICHTEN", "INNENANSICHTEN", None)


def set_attachment(real_estate, attachment):
    """Adds an attachment to the real estate."""

    dom = attachment.to_dom()
    dom.location = "REMOTE"
    dom.daten.pfad = BASE_URL.format(attachment.id)
    real_estate.anhaenge.anhang.append(dom)


def set_all_attachments(orm_id, real_estate):
    """Sets all attachments to the real estate."""

    for attachment in Anhang.by_immobilie(orm_id):
        set_attachment(real_estate, attachment)


def set_attachments(orm_id, real_estate, attachments):
    """Sets desired amount of attachments."""

    for number, attachment in enumerate(Anhang.by_immobilie(orm_id)):
        if number >= attachments:
            break

        set_attachment(real_estate, attachment)


def set_titlepic(orm_id, real_estate):
    """Sets the title picture."""

    for group in TITLEPIC_SEARCH_GROUPS:
        if group is None:
            group_selector = True
        else:
            group_selector = Anhang.gruppe == group

        try:
            anhang = Anhang.get((Anhang.immobilie == orm_id) & group_selector)
        except Anhang.DoesNotExist:
            continue

        set_attachment(real_estate, anhang)
        break


def set_free_texts(real_estate, freitexte):
    """Sets free texts on the real estate."""

    if freitexte:
        # Iff object description is missing,
        # replace it with the three-liner.
        if real_estate.freitexte:
            if not real_estate.freitexte.objektbeschreibung:
                real_estate.freitexte.objektbeschreibung = (
                    real_estate.freitexte.dreizeiler
                )
    else:
        real_estate.freitexte = None


class Selections(Enum):
    """Specifies sleection options."""

    FREITEXTE = "freitexte"
    TITLEPIC = "titlepic"
    N_ATTS = "atts"  # Some attachments
    ALLATTS = "allatts"  # All attachments


class RealEstateDataSelector:
    """Class that filters real estates of a user."""

    def __init__(self, real_estates, selections=None):
        """Initializes with a real estate,
        selection options and a picture limit.
        """
        self.real_estates = real_estates
        self.selections = selections or tuple()
        self.natts = compile_("(\\d)" + Selections.N_ATTS.value)

    def __iter__(self):
        """Returns real estates limited to the selections."""
        allatts = self.allatts
        attachments = self.attachments
        titlepic = self.titlepic

        for orm, dom in self.real_estates:
            # Discard previouly cached attachments.
            dom.anhaenge = anhaenge()

            if allatts:
                set_all_attachments(orm.id, dom)
            elif attachments is not None:
                set_attachments(orm.id, dom, attachments)
            elif titlepic:
                set_titlepic(orm.id, dom)

            set_free_texts(dom, self.freitexte)
            yield (orm, dom)

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
            match = self.natts.fullmatch(selection)

            if match is not None:
                try:
                    return int(match.group(1))
                except ValueError:
                    raise InvalidAttachmentLimit(selection) from None

        return None
