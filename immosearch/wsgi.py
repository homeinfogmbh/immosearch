"""WSGI-environ interpreter"""

from traceback import format_exc

from peewee import DoesNotExist
from urllib.parse import unquote

from homeinfo.lib.wsgi import WsgiApp, OK, Error, InternalServerError
from openimmo import factories
from openimmodb3.db import Attachment, Immobilie

from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, InvalidOptionsCount, OptionAlreadySet,\
    InvalidParameterError, UserNotAllowed, InvalidAuthenticationOptions,\
    InvalidCredentials, HandlersExhausted, NotAnInteger, NoDataCached, Caching
from .config import core
from .filter import RealEstateSieve
from .selector import RealEstateDataSelector
from .sort import RealEstateSorter
from .pager import Pager
from .attachments import AttachmentSelector, AttachmentLoader
from time import sleep
from threading import Thread

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
    ATTACHMENTS = 'attachments'
    PAGING = 'paging'


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
        self._cache = None
        caching = Thread(target=self._update_cache, args=[3600])
        caching.daemon = True
        caching.start()

    def _reset(self):
        """Resets the controller"""
        self._handler_opened = False

        self._filters = None
        self._sort_options = None
        self._includes = None
        self._scaling = None
        self._auth_token = None

        # Attachment selection
        self._attachment_indexes = None
        self._attachment_titles = None
        self._attachment_groups = None

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

    def __update_cache(self):
        """Re-cache user data in background"""
        self._cache = {}
        for user in ImmoSearchUser.select().where(
                ImmoSearchUser.enabled == 1):
            real_estates = [
                i.immobilie for i in Immobilie.by_cid(user.cid)]
            self._cache[user.cid] = real_estates

    def _update_cache(self, interval):
        """Re-cache user data in background"""
        while True:
            sleep(interval)
            self.__update_cache()

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
            value = unquote(qd[key])
            if key == Operations.AUTH_TOKEN:
                self._auth(value)
            elif key == Operations.INCLUDE:
                self._include(value)
            elif key == Operations.FILTER:
                self._filter(value)
            elif key == Operations.SORT:
                self._sort(value)
            elif key == Operations.ATTACHMENTS:
                self._attachments(value)
            elif key == Operations.PAGING:
                self._paging(value)
            # Ignore jQuery anti-cache timestamp
            elif key == '_':
                continue
            else:
                raise InvalidParameterError(key)

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

    def _attachments(self, value):
        """Generate scaling data"""
        attachment_opts = value.split(Separators.OPTION)
        if len(attachment_opts) < 1:
            raise InvalidOptionsCount()
        else:
            for attachment_opt in attachment_opts:
                split_option = attachment_opt.split(Separators.ATTR)
                option = split_option[0]
                value = Separators.ATTR.join(split_option[1:])
                if option == 'select':
                    if self._attachment_index is not None:
                        raise OptionAlreadySet(option, self._attachment_index)
                    elif self._attachment_title is not None:
                        raise OptionAlreadySet(option, self._attachment_title)
                    elif self._attachment_group is not None:
                        raise OptionAlreadySet(option, self._attachment_group)
                    try:
                        n = int(value)
                    except (ValueError, TypeError):
                        filter_str = value.replace('"', '')
                        if filter_str.startswith('%'):
                            self._attachment_group = filter_str.replace(
                                '%', '').upper()
                        else:
                            self._attachment_title = filter_str
                    else:
                        self._attachment_index = n
                else:
                    raise InvalidParameterError(option)

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
        if not self._cache:
            raise Caching()
        elif self._chkuser(user):
            try:
                real_estates = self._cache[user.cid]
            except KeyError:
                raise NoDataCached(user.cid)
            else:
                # Filter real estates
                real_estates = RealEstateSieve(real_estates, self._filters)
                # Select appropriate data
                real_estates = RealEstateDataSelector(
                    real_estates, selections=self._includes)
                # Sort real estates
                real_estates = RealEstateSorter(
                    real_estates, self._sort_options)
                # Page result
                real_estates = Pager(
                    real_estates, limit=self._page_size, page=self._page)
                # Generate realtor
                realtor = factories.anbieter(
                    str(user.cid), user.name, str(user.cid))
                # Manage attachments for each real estate
                for real_estate in real_estates:
                    if real_estate.anhaenge:
                        attachments = real_estate.anhaenge.anhang
                        # 1) Select attachments
                        attachments = AttachmentSelector(
                            attachments,
                            indexes=self._attachment_indexes,
                            titles=self._attachment_titles,
                            groups=self._attachment_groups)
                        # 4) Load attachments
                        attachments = AttachmentLoader(
                            attachments, self.user.max_bytes, self._scaling)
                        # 5) Set manipulated attachments on real estate
                        real_estate.anhaenge.anhang = [a for a in attachments]
                    realtor.immobilie.append(real_estate)
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
