"""WSGI app."""

from enum import Enum
from functools import lru_cache
from subprocess import CalledProcessError, check_output
from urllib.parse import unquote

from peewee import DoesNotExist
from pyxb import PyXBException

from filedb import FileError
from homeinfo.crm import Customer
from wsgilib import XML, OK, Binary, InternalServerError, RequestHandler
from openimmo import factories, openimmo
from openimmodb import Immobilie, Anhang

from immosearch.errors import NoSuchCustomer, InvalidPathLength, \
    InvalidPathNode, InvalidOptionsCount, NotAnInteger, \
    InvalidParameterError, UserNotAllowed, AttachmentNotFound
from immosearch.filter import RealEstateSieve
from immosearch.orm import Blacklist
from immosearch.pager import Pager
from immosearch.selector import RealEstateDataSelector
from immosearch.sort import RealEstateSorter

__all__ = ['ImmoSearchHandler']


def get_includes(value):
    """Select options."""

    for include in value.split(Separators.OPTION.value):
        yield include


def get_sorting(value):
    """Generate sorting data."""

    for sort_option in value.split(Separators.OPTION.value):
        try:
            key, mode = sort_option.split(Separators.ATTR.value)
        except ValueError:
            key = sort_option
            desc = False
        else:
            desc = mode == 'desc'

        yield (key, desc)


def get_paging(value):
    """Generate scaling data."""

    paging_opts = value.split(Separators.OPTION.value)

    if len(paging_opts) != 2:
        raise InvalidOptionsCount() from None

    limit = None
    page = None

    for paging_opt in paging_opts:
        option, *values = paging_opt.split(Separators.ATTR.value)
        value = Separators.ATTR.value.join(values)

        if option == 'limit':
            try:
                limit = int(value)
            except (ValueError, TypeError):
                raise NotAnInteger(value) from None
        elif option == 'page':
            try:
                page = int(value)
            except (ValueError, TypeError):
                raise NotAnInteger(value) from None
        else:
            raise InvalidParameterError(option) from None

    if limit is None or page is None:
        return None

    return (limit, page)


def get_real_estates(customer):
    """Returns real estates for the respective customer."""

    for real_estate in Immobilie.by_customer(customer):
        yield (real_estate, real_estate.to_dom())


def filter_real_estates(real_estates, filters, sort, paging, includes):
    """Perform sieving, sorting and rendering."""

    if filters is not None:
        real_estates = RealEstateSieve(real_estates, filters)

    real_estates = RealEstateDataSelector(real_estates, selections=includes)

    if sort is not None:
        real_estates = RealEstateSorter(real_estates, sort)

    if paging is not None:
        page_size, page_num = paging
        real_estates = Pager(real_estates, limit=page_size, page=page_num)

    return real_estates


def set_paging(anbieter, paging):
    """Sets paging information."""

    if paging is not None:
        page_size, page_num = paging
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(page_size, feldname='page_size'))
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(page_num, feldname='page_num'))


def set_fortune(anbieter):
    """Sets a random message of the day (easter egg)."""

    try:
        fortune = check_output('/usr/games/fortune').decode().strip()
    except (FileNotFoundError, CalledProcessError, ValueError):
        pass
    else:
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(fortune, feldname='motd'))


def gen_anbieter(customer, paging):
    """Generates an openimmo.anbieter DOM."""

    anbieter = factories.anbieter(
        str(customer.id), customer.name, str(customer.id))
    set_paging(anbieter, paging)
    set_fortune(anbieter)
    return anbieter


class Separators(Enum):
    """Special separation characters."""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = ':'
    PATH = '/'


class Operations(Enum):
    """Valid query operations."""

    FILTER = 'filter'
    INCLUDE = 'include'
    SORT = 'sort'
    PAGING = 'paging'
    NOCACHE = 'nocache'


class PathNodes(Enum):
    """Valid path nodes."""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


class ImmoSearchHandler(RequestHandler):
    """HAndles requests for ImmoSearch."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    @property
    @lru_cache(maxsize=1)
    def cid(self):
        """Extracts the customer ID from the query path."""
        path = self.path

        if len(path) > 1:
            if path[1] == PathNodes.CUSTOMER.value:
                if len(path) == 3:
                    cid = path[2]

                    try:
                        return int(cid)
                    except ValueError:
                        raise NotAnInteger(cid) from None

                raise InvalidPathLength(len(path)) from None

            raise InvalidPathNode(path[1]) from None

    @property
    @lru_cache(maxsize=1)
    def customer(self):
        """Returns the respective customer."""
        try:
            return Customer.get(Customer.id == self.cid)
        except DoesNotExist:
            return NoSuchCustomer(self.cid)

    @property
    @lru_cache(maxsize=1)
    def aid(self):
        """Extracts an attachment identifier from the path."""
        path = self.path

        try:
            mode = path[1]
        except IndexError:
            raise InvalidPathLength(len(path)) from None

        if mode == 'attachment':
            try:
                attachment_id = path[2]
            except IndexError:
                raise InvalidPathLength(len(path)) from None

            try:
                return int(attachment_id)
            except (TypeError, ValueError):
                raise NotAnInteger(attachment_id) from None

        raise InvalidPathNode(mode) from None

    @property
    @lru_cache(maxsize=1)
    def attachment(self):
        """REturns the respective attachment."""
        try:
            return Anhang.get(Anhang.id == self.aid)
        except DoesNotExist:
            raise AttachmentNotFound() from None

    @property
    @lru_cache(maxsize=1)
    def options(self):
        """Parses the query dictionary for options."""
        filters = None
        sort = None
        paging = None
        includes = None

        for key, value in self.query.items():
            try:
                value = unquote(value)
            except TypeError:
                value = None

            if key == Operations.INCLUDE.value:
                includes = tuple(get_includes(value))
            elif key == Operations.FILTER.value:
                filters = value
            elif key == Operations.SORT.value:
                sort = tuple(get_sorting(value))
            elif key == Operations.PAGING.value:
                paging = get_paging(value)

        return (filters, sort, paging, includes)

    @property
    def anbieter(self):
        """Gets real estates (XML) data."""
        filters, sort, paging, includes = self.options
        customer = self.customer

        try:
            Blacklist.get(Blacklist.customer == customer)
        except DoesNotExist:
            real_estates = filter_real_estates(
                get_real_estates(customer), filters, sort, paging, includes)
            anbieter = gen_anbieter(customer, paging)
            self.set_validated_real_estates(anbieter, real_estates)
            return XML(anbieter)
        else:
            return UserNotAllowed(self.cid)

    @property
    def attachments(self):
        """Returns the queried attachment."""
        if self.query.get('sha256sum', False):
            try:
                return OK(self.attachment.sha256sum)
            except FileError:
                return InternalServerError('Could not get file checksum.')

        try:
            return Binary(self.attachment.data)
        except FileError:
            return InternalServerError('Could not find file for attachment.')


    def set_validated_real_estates(self, anbieter, real_estates):
        """Sets validated real estates."""
        flawed = openimmo.user_defined_extend()
        count = 0

        for count, (_, dom) in enumerate(real_estates, start=1):
            try:
                dom.toxml()
            except PyXBException as error:
                self.logger.error('Failed to serialize "{}".'.format(
                    dom.objektnr_extern))
                feld = openimmo.feld(
                    name='Flawed real estate', wert=dom.objektnr_extern)
                feld.typ.append(str(error))
                flawed.feld.append(feld)
            else:
                anbieter.immobilie.append(dom)

        if flawed.feld:
            anbieter.user_defined_extend.append(flawed)

        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(count, feldname='count'))

    def get(self):
        """Main method to call."""
        try:
            mode = self.path[1]
        except IndexError:
            raise InvalidPathLength(len(self.path)) from None

        if mode == 'attachment':
            return self.attachments
        elif mode in ('customer', 'realestates'):
            return self.anbieter

        raise InvalidPathNode(mode) from None
