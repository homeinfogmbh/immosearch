"""WSGI-environ interpreter"""

from traceback import format_exc

from peewee import DoesNotExist
from urllib.parse import unquote

from homeinfo.lib.wsgi import WsgiApp, OK, Error, InternalServerError
from openimmo import factories
from openimmodb3.db import Attachment

from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, InvalidOptionsCount, InvalidParameterError,\
    UserNotAllowed, InvalidAuthenticationOptions, InvalidCredentials,\
    NotAnInteger
from .cache import CacheManager
from .config import core
from .filter import RealEstateSieve
from .selector import RealEstateDataSelector
from .sort import RealEstateSorter
from .pager import Pager

__all__ = ['RealEstateController', 'AttachmentController']


class Separators():
    """Special separation characters"""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = ':'
    PATH = '/'


class Operations():
    """Valid query operations"""

    AUTH_TOKEN = 'auth_token'
    FILTER = 'filter'
    INCLUDE = 'include'
    SORT = 'sort'
    PAGING = 'paging'
    NOCACHE = 'nocache'


class PathNodes():
    """Valid path nodes"""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


class RealEstateController(WsgiApp):
    """Class that interprets and translates WSGI environment
    variables into a filter, sort and scaling queries
    """

    DEBUG = True

    def __init__(self):
        """Initializes the WSGI application for CORS"""
        super().__init__(cors=True)
        self._cache = {}

    def _cid(self, path):
        """Extracts the customer ID from the query path"""
        if len(path) > 1:
            if path[1] == PathNodes.CUSTOMER:
                if len(path) == 3:
                    cid_str = path[2]
                    try:
                        cid = int(cid_str)
                    except ValueError:
                        raise InvalidCustomerID(cid_str)
                    else:
                        return cid
                else:
                    raise InvalidPathLength(len(path))
            else:
                raise InvalidPathNode(path[1])

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

    def _parse_opts(self, qd):
        """Parses the query dictionary for options"""
        auth_token = None
        cache = True
        filters = None
        includes = None
        sort = None
        paging = None
        for key in qd:
            if key == Operations.NOCACHE:
                cache = False
            else:
                value = unquote(qd[key])
                if key == Operations.AUTH_TOKEN:
                    auth_token = self._auth(value)
                elif key == Operations.INCLUDE:
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
        return (auth_token, cache, filters, includes, sort, paging)

    def _data(self, user, auth_token, cache, filters, includes, sort, paging):
        """Perform sieving, sorting and rendering"""
        self._parse()
        if not user.enabled:
            raise UserNotAllowed(user.cid)
        elif user.authenticate(auth_token):
            # Cache real estates
            if not cache:
                self._cache.pop(user.cid, None)
            re_gen = CacheManager(user, self._cache)
            # Filter real estates
            if filters is not None:
                re_gen = RealEstateSieve(re_gen, filters)
            # Select appropriate data
            if includes is not None:
                re_gen = RealEstateDataSelector(re_gen, selections=includes)
            # Sort real estates
            if sort is not None:
                re_gen = RealEstateSorter(re_gen, sort)
            # Page result
            if paging is not None:
                page_size, pageno = paging
                re_gen = Pager(re_gen, limit=page_size, page=pageno)
            # Generate real estate list from real estate generator
            immobilie = [i for i in re_gen]
            # Generate realtor
            anbieter = factories.anbieter(
                str(user.cid), user.name, str(user.cid),
                immobilie=immobilie)
            return anbieter
        else:
            raise InvalidCredentials()

    def get(self, environ):
        """Main method to call"""
        query_string = self.query_string(environ)
        qd = self.qd(query_string)
        path_info = self.path_info(environ)
        path = self.path(path_info)
        options = self._parse_opts(qd)
        cid = self._cid(path)
        user = self._user(cid)
        try:
            result = self._data(user, *options)
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


class AttachmentController(WsgiApp):
    """Controller for attachment queries"""

    DEBUG = True

    def __init__(self):
        """Initializes the WSGI application for CORS"""
        super().__init__(cors=True)

    def _identifier(self, path):
        """Extracts the customer ID from the query path"""
        if len(path) > 1:
            if path[1] == 'attachment':
                if len(path) == 3:
                    return path[2]
                else:
                    raise InvalidPathLength(len(path))
            else:
                raise InvalidPathNode(path[1])

    def get(self, environ):
        """Returns the queried attachment"""
        path_info = self.path_info(environ)
        path = self.path(path_info)
        ident = self._identifier(path)
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
                mimetype, data = a.data
                return OK(data, content_type=mimetype, charset=None)
