"""WSGI app."""

from enum import Enum
from urllib.parse import unquote

from peewee import DoesNotExist
from pyxb import PyXBException

from filedb.http import FileError
from homeinfo.crm import Customer
from wsgilib import JSON, XML, OK, Binary, InternalServerError, RequestHandler
from openimmo import factories, openimmo
from openimmodb import Anhang

from immosearch.cache import RealEstateCache
from immosearch.errors import NoSuchCustomer, InvalidPathLength, \
    InvalidPathNode, InvalidOptionsCount, NotAnInteger, \
    InvalidParameterError, UserNotAllowed, AttachmentNotFound
from immosearch.filter import RealEstateSieve
from immosearch.orm import Blacklist
from immosearch.pager import Pager
from immosearch.selector import RealEstateDataSelector
from immosearch.sort import RealEstateSorter

__all__ = ['ImmoSearchHandler']


CACHE = {}


def get_real_estates(customer):
    """Returns real estates for the respective customer."""

    try:
        return CACHE[customer]
    except KeyError:
        cache = RealEstateCache(customer)
        CACHE[customer] = cache
        return cache


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
    else:
        limit = None
        page = None

        for paging_opt in paging_opts:
            split_option = paging_opt.split(Separators.ATTR.value)
            option = split_option[0]
            value = Separators.ATTR.value.join(split_option[1:])

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

        if limit is not None and page is not None:
            return (limit, page)


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
    def _cid(self):
        """Extracts the customer ID from the query path."""
        path = self.path

        if len(path) > 1:
            if path[1] == PathNodes.CUSTOMER.value:
                if len(path) == 3:
                    cid = path[2]

                    try:
                        cid = int(cid)
                    except ValueError:
                        raise NotAnInteger(cid) from None
                    else:
                        return cid

                raise InvalidPathLength(len(path)) from None

            raise InvalidPathNode(path[1]) from None

    @property
    def _aid(self):
        """Extracts an attachment identifier from the path."""
        path = self.path

        try:
            mode = path[1]
        except IndexError:
            raise InvalidPathLength(len(path)) from None
        else:
            if mode == 'attachment':
                try:
                    attachment_id = path[2]
                except IndexError:
                    raise InvalidPathLength(len(path)) from None
                else:
                    return attachment_id

            raise InvalidPathNode(mode) from None

    @property
    def _options(self):
        """Parses the query dictionary for options."""
        filters = None
        sort = None
        paging = None
        includes = None
        json = False

        for key in self.query:
            try:
                value = unquote(self.query[key])
            except TypeError:
                value = None

            if key == Operations.INCLUDE.value:
                includes = [i for i in get_includes(value)]
            elif key == Operations.FILTER.value:
                filters = value
            elif key == Operations.SORT.value:
                sort = [i for i in get_sorting(value)]
            elif key == Operations.PAGING.value:
                paging = get_paging(value)
            elif key == 'json':
                try:
                    json = int(value)
                except (TypeError, ValueError):
                    json = None
            # Ignore jQuery anti-cache timestamp
            elif key == '_':
                continue
            # else:
            #    raise InvalidParameterError(key)
            # XXX: Fix Niko's obsolete params
            else:
                continue

        return (filters, sort, paging, includes, json)

    @property
    def _realestates(self):
        """Gets real estates (XML) data."""
        filters, sort, paging, includes, json = self._options

        try:
            customer = Customer.get(Customer.id == self._cid)
        except DoesNotExist:
            return NoSuchCustomer(self._cid)

        try:
            Blacklist.get(Blacklist.customer == customer)
        except DoesNotExist:
            anbieter = self._data(customer, filters, sort, paging, includes)

            if json is False:
                return XML(anbieter)

            return JSON(anbieter.todict(), indent=json)
        else:
            return UserNotAllowed(self._cid)

    @property
    def _attachments(self):
        """Returns the queried attachment."""
        try:
            ident = int(self._aid)
        except (TypeError, ValueError):
            raise NotAnInteger(self._aid) from None
        else:
            try:
                anhang = Anhang.get(Anhang.id == ident)
            except DoesNotExist:
                raise AttachmentNotFound() from None
            else:
                if self.query.get('sha256sum', False):
                    try:
                        return OK(anhang.sha256sum)
                    except FileError:
                        return InternalServerError(
                            'Could not get file checksum')

                try:
                    return Binary(anhang.data)
                except FileError:
                    return InternalServerError(
                        'Could not find file for attachment')

    def _data(self, customer, filters, sort, paging, includes):
        """Perform sieving, sorting and rendering."""
        anbieter = factories.anbieter(
            str(customer.id), customer.name, str(customer.id))
        real_estates = get_real_estates(customer)

        if filters is not None:
            real_estates = RealEstateSieve(real_estates, filters)

        real_estates = RealEstateDataSelector(
            customer, real_estates, selections=includes)

        if sort is not None:
            real_estates = RealEstateSorter(real_estates, sort)

        if paging is not None:
            page_size, page_num = paging
            real_estates = Pager(real_estates, limit=page_size, page=page_num)
            anbieter.user_defined_simplefield.append(
                openimmo.user_defined_simplefield(
                    page_size, feldname='page_size'))
            anbieter.user_defined_simplefield.append(
                openimmo.user_defined_simplefield(
                    page_num, feldname='page_num'))

        # Generate real estate list from real estate generator
        flawed = openimmo.user_defined_extend()

        for count, real_estate in enumerate(real_estates):
            try:
                real_estate.toxml()
            except PyXBException as error:
                self.logger.error('Failed to serialize "{}".'.format(
                    real_estate.objektnr_extern))
                feld = openimmo.feld(
                    name='Flawed real estate',
                    wert=real_estate.objektnr_extern)
                feld.typ.append(str(error))
                flawed.feld.append(feld)
            else:
                anbieter.immobilie.append(real_estate)

        if flawed.feld:
            anbieter.user_defined_extend.append(flawed)

        try:
            count += 1
        except UnboundLocalError:
            count = 0

        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(count, feldname='count'))

        return anbieter

    def get(self):
        """Main method to call."""
        path = self.path

        try:
            mode = path[1]
        except IndexError:
            raise InvalidPathLength(len(path)) from None
        else:
            if mode == 'attachment':
                return self._attachments
            elif mode in ['customer', 'realestates']:
                return self._realestates

            raise InvalidPathNode(mode) from None
