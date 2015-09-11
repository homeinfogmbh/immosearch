"""WSGI-environ interpreter"""

from traceback import format_exc

from peewee import DoesNotExist
from urllib.parse import unquote

from homeinfo.lib.wsgi import WsgiApp, OK, Error, InternalServerError
from openimmo import factories
from openimmodb3.db import Attachment

from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, InvalidOptionsCount, OptionAlreadySet,\
    InvalidParameterError, UserNotAllowed, InvalidAuthenticationOptions,\
    InvalidCredentials, HandlersExhausted, NotAnInteger
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
        self._reset()
        self._cache = {}

    def _reset(self):
        """Resets the controller"""
        self._handler_opened = False

        self._filters = None
        self._sort_options = None
        self._includes = None
        self._auth_token = None
        self._nocache = None

        # Paging
        self._page_size = None
        self._page = None

    @property
    def cid(self):
        """Extracts the customer ID from the query path"""
        if len(self.path) > 1:
            if self.path[1] == PathNodes.CUSTOMER:
                if len(self.path) == 3:
                    cid_str = self.path[2]
                    try:
                        cid = int(cid_str)
                    except ValueError:
                        raise InvalidCustomerID(cid_str)
                    else:
                        return cid
                else:
                    raise InvalidPathLength(len(self.path))
            else:
                raise InvalidPathNode(self.path[1])

    @property
    def user(self):
        """Returns the user"""
        cid = self.cid
        try:
            user = ImmoSearchUser.get(ImmoSearchUser.customer == cid)
        except DoesNotExist:
            raise InvalidCustomerID(str(cid))
        else:
            return user

    def _chkhandlers(self, user):
        """Check for used handlers"""
        if user.current_handlers < user.max_handlers:
            user.current_handlers += 1
            self._handler_opened = True
            return True
        else:
            raise HandlersExhausted(user.max_handlers)

    def _chkuser(self, user):
        """Check whether user is allowed to retrieve real estates"""
        if user is None:
            return False
        elif user.enabled:
            user = self.user
            if user.protected:
                auth_token = self._auth_token
                if auth_token:
                    if user.auth_token:
                        if auth_token == user.auth_token:
                            return self._chkhandlers(user)
                        else:
                            raise InvalidCredentials()
                    else:
                        raise InvalidCredentials()
                else:
                    raise InvalidCredentials()
            else:
                return self._chkhandlers(user)
        else:
            return False

    def _parse(self):
        """Parses a URI for query commands"""
        qd = self.qd
        for key in qd:
            if key == Operations.NOCACHE:
                self._nocache = True
            else:
                value = unquote(qd[key])
                if key == Operations.AUTH_TOKEN:
                    self._auth(value)
                elif key == Operations.INCLUDE:
                    self._include(value)
                elif key == Operations.FILTER:
                    self._filter(value)
                elif key == Operations.SORT:
                    self._sort(value)
                elif key == Operations.PAGING:
                    self._paging(value)
                # Ignore jQuery anti-cache timestamp
                elif key == '_':
                    continue
                # else:
                #    raise InvalidParameterError(key)
                # XXX: Fix Niko's obsolete params
                else:
                    continue

    def _auth(self, value):
        """Extract authentication data"""
        if self._auth_token is None:
            auth_opts = value.split(Separators.OPTION)
            if len(auth_opts) != 1:
                raise InvalidAuthenticationOptions()    # Do not propagate data
            else:
                self._auth_token = auth_opts[0]
        else:
            raise OptionAlreadySet(Operations.AUTH_TOKEN, '*****')

    def _include(self, value):
        """Select options"""
        if self._includes is None:
            self._includes = []
            includes = value.split(Separators.OPTION)
            for include in includes:
                self._includes.append(include)
        else:
            raise OptionAlreadySet(Operations.INCLUDE, str(self._includes))

    def _filter(self, value):
        """Generate filtering data"""
        if self._filters is None:
            self._filters = value
        else:
            raise OptionAlreadySet(Operations.FILTER, str(self._filters))

    def _sort(self, value):
        """Generate filtering data"""
        if self._sort_options is None:
            self._sort_options = []
            for sort_option in value.split(Separators.OPTION):
                try:
                    key, mode = sort_option.split(Separators.ATTR)
                except ValueError:
                    key = sort_option
                    mode = False
                else:
                    if mode == 'desc':
                        mode = True
                    else:
                        mode = False
                self._sort_options.append((key, mode))
        else:
            raise OptionAlreadySet(Operations.SORT, str(self._sort_options))

    def _paging(self, value):
        """Generate scaling data"""
        paging_opts = value.split(Separators.OPTION)
        if len(paging_opts) != 2:
            raise InvalidOptionsCount()
        else:
            for paging_opt in paging_opts:
                split_option = paging_opt.split(Separators.ATTR)
                option = split_option[0]
                value = Separators.ATTR.join(split_option[1:])
                if option == 'limit':
                    try:
                        limit = int(value)
                    except (ValueError, TypeError):
                        raise NotAnInteger(value)
                    else:
                        self._page_size = limit
                elif option == 'page':
                    try:
                        page = int(value)
                    except (ValueError, TypeError):
                        raise NotAnInteger(value)
                    else:
                        self._page = page
                else:
                    raise InvalidParameterError(option)

    @property
    def _data(self):
        """Perform sieving, sorting and rendering"""
        user = self.user
        self._parse()
        if self._chkuser(user):
            # Cache real estates
            if self._nocache:
                self._cache.pop(user.cid)
            cache_manager = CacheManager(user, self._cache)
            # Filter real estates
            real_estate_sieve = RealEstateSieve(cache_manager, self._filters)
            # Select appropriate data
            real_estate_selector = RealEstateDataSelector(
                real_estate_sieve, selections=self._includes)
            # Sort real estates
            real_estate_sorter = RealEstateSorter(
                real_estate_selector, self._sort_options)
            # Page result
            real_estate_pager = Pager(
                real_estate_sorter, limit=self._page_size, page=self._page)
            # Generate real estate list
            immobilie = [i for i in real_estate_pager]
            # Generate realtor
            realtor = factories.anbieter(
                str(user.cid), user.name, str(user.cid),
                immobilie=immobilie)
            return realtor
        else:
            raise UserNotAllowed(self.cid)

    def get(self):
        """Main method to call"""
        try:
            result = self._data
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
        finally:
            if self._handler_opened:
                self.user.current_handlers += -1
            self._reset()


class AttachmentController(WsgiApp):
    """Controller for attachment queries"""

    DEBUG = True

    def __init__(self):
        """Initializes the WSGI application for CORS"""
        super().__init__(cors=True)

    @property
    def _identifier(self):
        """Extracts the customer ID from the query path"""
        if len(self.path) > 1:
            if self.path[1] == 'attachment':
                if len(self.path) == 3:
                    return self.path[2]
                else:
                    raise InvalidPathLength(len(self.path))
            else:
                raise InvalidPathNode(self.path[1])

    def get(self):
        """Returns the queried attachment"""
        try:
            ident = int(self._identifier)
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
