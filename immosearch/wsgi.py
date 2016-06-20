"""WSGI app"""

from traceback import format_exc
from contextlib import suppress

from peewee import DoesNotExist
from urllib.parse import unquote

from filedb.http import FileError
from homeinfo.crm import Customer
from homeinfo.lib.misc import Enumeration
from homeinfo.lib.wsgi import OK, Error, InternalServerError, handler, \
    RequestHandler, WsgiApp
from openimmo import factories
from openimmodb3.db import Attachment, Immobilie

from .orm import Blacklist
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, InvalidOptionsCount, InvalidParameterError,\
    UserNotAllowed, InvalidAuthenticationOptions, NotAnInteger
# from .cache import CacheManager
from .lib import RealEstate
from .config import core
from .filter import RealEstateSieve
from .selector import RealEstateDataSelector
from .sort import RealEstateSorter
from .pager import Pager

__all__ = ['ImmoSearch']


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


class ImmoSearchRequestHandler(RequestHandler):
    """HAndles requests for ImmoSearch"""

    def __init__(self, environ, cors, date_format, debug):
        super().__init__(environ, cors, date_format, debug)
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
                        raise InvalidCustomerID(cid)
                    else:
                        return cid
                else:
                    raise InvalidPathLength(len(path))
            else:
                raise InvalidPathNode(path[1])

    @property
    def _aid(self):
        """Extracts an attachment identifier from the path"""
        path = self.path

        try:
            mode = path[1]
        except IndexError:
            raise InvalidPathLength(len(path))
        else:
            if mode == 'attachment':
                try:
                    attachment_id = path[2]
                except IndexError:
                    raise InvalidPathLength(len(path))
                else:
                    return attachment_id
            else:
                raise InvalidPathNode(mode)

    def _user(self, cid):
        """Returns the user"""
        try:
            user = ImmoSearchUser.get(ImmoSearchUser.customer == cid)
        except DoesNotExist:
            raise InvalidCustomerID(str(cid))
        else:
            return user

    def _auth(self, value):
        """Extract authentication data"""
        auth_opts = value.split(Separators.OPTION)

        if len(auth_opts) != 1:
            raise InvalidAuthenticationOptions()    # Do not propagate data
        else:
            return auth_opts[0]

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
            raise InvalidOptionsCount()
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
                        raise NotAnInteger(value)
                elif option == 'page':
                    try:
                        page = int(value)
                    except (ValueError, TypeError):
                        raise NotAnInteger(value)
                else:
                    raise InvalidParameterError(option)

            if limit is not None and page is not None:
                return (limit, page)

    @property
    def _options(self):
        """Parses the query dictionary for options"""
        qd = self.query_dict

        filters = None
        sort = None
        paging = None
        includes = None

        for key in qd:
            with suppress(TypeError):
                value = unquote(qd[key])
            if key == Operations.INCLUDE:
                includes = [i for i in self._include(value)]
            elif key == Operations.FILTER:
                filters = value
            elif key == Operations.SORT:
                sort = [i for i in self._sort(value)]
            elif key == Operations.PAGING:
                paging = self._paging(value)
            # Ignore jQuery anti-cache timestamp
            elif key == '_':
                continue
            # else:
            #    raise InvalidParameterError(key)
            # XXX: Fix Niko's obsolete params
            else:
                continue

        return (filters, sort, paging, includes)

    @property
    def _realestates(self):
        """Gets real estates (XML) data"""
        options = self._options

        try:
            customer = Customer.get(Customer.id == self._cid)
        except DoesNotExist:
            return NoSuchCustomer(cid)

        try:
            blacklist_entry = Blacklist.get(Blacklist.customer == customer)
        except DoesNotExist:
            try:
                result = self._data(customer, *options)
            except RenderableError as r:
                status = r.status or 400
                return Error(r, content_type='application/xml', status=status)
            except:
                msg = 'Internal Server Error :-('

                if core.get('DEBUG', False):
                    msg = '\n'.join([msg, format_exc()])

                return InternalServerError(msg)
            else:
                return OK(result, content_type='application/xml')
        else:
            return UserNotAllowed(cid)

    @property
    def _attachments(self):
        """Returns the queried attachment"""
        ident = self._aid

        try:
            ident = int(ident)
        except (TypeError, ValueError):
            return Error('Attachment ID must be an integer')
        else:
            try:
                a = Attachment.get(Attachment.id == ident)
            except DoesNotExist:
                return Error('Attachment not found')
            else:
                try:
                    mimetype, data = a.data
                except FileError:
                    return InternalServerError(
                        'Could not find file for attachment')
                else:
                    return OK(data, content_type=mimetype, charset=None)

    def _data(self, customer, filters, sort, paging, includes):
        """Perform sieving, sorting and rendering"""
        re_gen = (RealEstate(i) for i in Immobilie.by_cid(customer.id))

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
        immobilie = [i.dom for i in re_gen]

        # Generate realtor
        anbieter = factories.anbieter(
            str(customer.cid), customer.name, str(customer.cid),
            immobilie=immobilie)

        return anbieter

    def get(self):
        """Main method to call"""
        path = self.path

        try:
            mode = path[1]
        except IndexError:
            raise InvalidPathLength(len(path))
        else:
            if mode == 'attachment':
                return self._attachments
            elif mode in ['customer', 'realestates']:
                return self._realestates
            else:
                raise InvalidPathNode(mode)


@handler(ImmoSearchRequestHandler)
class ImmoSearch(WsgiApp):
    """ImmoSearch web application"""

    DEBUG = True

    def __init__(self):
        """Initializes the WSGI application for CORS"""
        super().__init__(cors=True)
