"""WSGI app"""

from peewee import DoesNotExist
from pydb import PyXBException
from urllib.parse import unquote

from filedb.http import FileError
from homeinfo.crm import Customer
from homeinfo.misc import Enumeration
from wsgilib import JSON, XML, OK, Binary, InternalServerError, RequestHandler
from openimmo import factories, openimmo
from openimmodb import Anhang, Immobilie

# from immosearch.cache import CacheManager
from immosearch.errors import NoSuchCustomer, InvalidPathLength, \
    InvalidPathNode, InvalidOptionsCount, NotAnInteger, \
    InvalidParameterError, UserNotAllowed, AttachmentNotFound
from immosearch.filter import RealEstateSieve
from immosearch.lib import RealEstate
from immosearch.orm import Blacklist
from immosearch.pager import Pager
from immosearch.selector import RealEstateDataSelector
from immosearch.sort import RealEstateSorter

__all__ = ['ImmoSearchHandler']


class Separators(Enumeration):
    """Special separation characters"""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = ':'
    PATH = '/'


class Operations(Enumeration):
    """Valid query operations"""

    FILTER = 'filter'
    INCLUDE = 'include'
    SORT = 'sort'
    PAGING = 'paging'
    NOCACHE = 'nocache'


class PathNodes(Enumeration):
    """Valid path nodes"""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


class ImmoSearchHandler(RequestHandler):
    """HAndles requests for ImmoSearch"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    @property
    def _cid(self):
        """Extracts the customer ID from the query path"""
        path = self.path

        if len(path) > 1:
            if path[1] == PathNodes.CUSTOMER:
                if len(path) == 3:
                    cid = path[2]

                    try:
                        cid = int(cid)
                    except ValueError:
                        raise NotAnInteger(cid) from None
                    else:
                        return cid
                else:
                    raise InvalidPathLength(len(path)) from None
            else:
                raise InvalidPathNode(path[1]) from None

    @property
    def _aid(self):
        """Extracts an attachment identifier from the path"""
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
            else:
                raise InvalidPathNode(mode) from None

    def _include(self, value):
        """Select options"""
        includes = value.split(Separators.OPTION)

        for include in includes:
            yield include

    def _sort(self, value):
        """Generate filtering data"""
        for sort_option in value.split(Separators.OPTION):
            try:
                key, mode = sort_option.split(Separators.ATTR)
            except ValueError:
                key = sort_option
                desc = False
            else:
                if mode == 'desc':
                    desc = True
                else:
                    desc = False

            yield (key, desc)

    def _paging(self, value):
        """Generate scaling data"""
        paging_opts = value.split(Separators.OPTION)
        if len(paging_opts) != 2:
            raise InvalidOptionsCount() from None
        else:
            limit = None
            page = None

            for paging_opt in paging_opts:
                split_option = paging_opt.split(Separators.ATTR)
                option = split_option[0]
                value = Separators.ATTR.join(split_option[1:])

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

    @property
    def _options(self):
        """Parses the query dictionary for options"""
        filters = None
        sort = None
        paging = None
        includes = None
        json = False

        for key in self.query:
            try:
                value = unquote(self.query[key])
            except (TypeError):
                value = None

            if key == Operations.INCLUDE:
                includes = [i for i in self._include(value)]
            elif key == Operations.FILTER:
                filters = value
            elif key == Operations.SORT:
                sort = [i for i in self._sort(value)]
            elif key == Operations.PAGING:
                paging = self._paging(value)
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
        """Gets real estates (XML) data"""
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
            else:
                return JSON(anbieter.todict(), indent=json)
        else:
            return UserNotAllowed(self._cid)

    @property
    def _attachments(self):
        """Returns the queried attachment"""
        try:
            ident = int(self._aid)
        except (TypeError, ValueError):
            raise NotAnInteger() from None
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
                else:
                    try:
                        return Binary(anhang.data)
                    except FileError:
                        return InternalServerError(
                            'Could not find file for attachment')

    def _data(self, customer, filters, sort, paging, includes):
        """Perform sieving, sorting and rendering"""
        re_gen = (RealEstate(i) for i in Immobilie.of(customer))

        # Filter real estates
        if filters is not None:
            re_gen = RealEstateSieve(re_gen, filters)

        # Select appropriate data
        re_gen = RealEstateDataSelector(re_gen, selections=includes)

        # Sort real estates
        if sort is not None:
            re_gen = RealEstateSorter(re_gen, sort)

        # Page result
        if paging is not None:
            page_size, pageno = paging
            re_gen = Pager(re_gen, limit=page_size, page=pageno)

        # Generate real estate list from real estate generator
        immobilie = []
        flawed = openimmo.user_defined_extend()

        for real_estate in re_gen:
            dom = real_estate.dom

            try:
                dom.toxml()
            except PyXBException as e:
                self.logger.error('Failed to serialize "{}".'.format(
                    dom.objektnr_extern))
                flawed.feld.append(openimmo.feld(
                    name='Flawed real estate',
                    wert=dom.objektnr_extern,
                    typ=str(e)))
            else:
                immobilie.append(dom)

        # Generate realtor
        anbieter = factories.anbieter(
            str(customer.id), customer.name, str(customer.id),
            immobilie=immobilie)

        # Append flawed data
        if flawed.feld:
            anbieter.user_defined_extend.append(flawed)

        return anbieter

    def get(self):
        """Main method to call"""
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
            else:
                raise InvalidPathNode(mode) from None
