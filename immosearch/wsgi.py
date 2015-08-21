"""WSGI-environ interpreter"""

from traceback import format_exc

from peewee import DoesNotExist
from urllib.parse import unquote

from homeinfo.lib.wsgi import WsgiController, OK, Error, InternalServerError
from openimmo import factories

from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, InvalidOptionsCount, InvalidRenderingResolution,\
    OptionAlreadySet, InvalidParameterError, UserNotAllowed,\
    InvalidAuthenticationOptions, InvalidCredentials, HandlersExhausted,\
    NotAnInteger
from .config import core
from .filter import UserRealEstateSieve
from .selector import RealEstateDataSelector
from .sort import RealEstateSorter
from .pager import Pager
from .attachments import AttachmentSelector, AttachmentLimiter,\
    AttachmentLoader
from homie.mods.is24.lib import MissingIdentifier

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
    SELECT = 'select'
    FILTER = 'filter'
    INCLUDE = 'include'
    SORT = 'sort'
    ATTACHMENTS = 'attachments'
    PAGING = 'paging'


class PathNodes():
    """Valid path nodes"""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


class RealEstateController(WsgiController):
    """Class that interprets and translates WSGI environment
    variables into a filter, sort and scaling queries
    """

    DEBUG = True

    def __init__(self, path_info, query_string):
        """Initializes the WSGI application with a query string"""
        super().__init__(path_info, query_string)
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

        # Attachment limits
        self._picture_limit = None
        self._floorplan_limit = None
        self._document_limit = None

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
        render_opts = value.split(Separators.OPTION)
        if len(render_opts) < 1:
            raise InvalidOptionsCount()
        else:
            for render_opt in render_opts:
                split_option = render_opt.split(Separators.ATTR)
                option = split_option[0]
                value = Separators.ATTR.join(split_option[1:])
                if option == 'scaling':
                    if self._scaling is None:
                        try:
                            str_x, str_y = value.split('x')
                        except ValueError:
                            raise InvalidRenderingResolution(value)
                        else:
                            try:
                                x = int(str_x)
                                y = int(str_y)
                            except:
                                raise InvalidRenderingResolution(value)
                            else:
                                self._scaling = (x, y)
                    else:
                        raise OptionAlreadySet(option, self._scaling)
                elif option == 'pictures':
                    if self._picture_limit is None:
                        try:
                            limit = int(value)
                        except (ValueError, TypeError):
                            raise NotAnInteger(value)
                        else:
                            self._picture_limit = limit
                    else:
                        raise OptionAlreadySet(option, self._picture_limit)
                elif option == 'floorplans':
                    if self._floorplan_limit is None:
                        try:
                            limit = int(value)
                        except (ValueError, TypeError):
                            raise NotAnInteger(value)
                        else:
                            self._floorplan_limit = limit
                    else:
                        raise OptionAlreadySet(option, self._floorplan_limit)
                elif option == 'documents':
                    if self._document_limit is None:
                        try:
                            limit = int(value)
                        except (ValueError, TypeError):
                            raise NotAnInteger(value)
                        else:
                            self._document_limit = limit
                    else:
                        raise OptionAlreadySet(option, self._document_limit)
                elif option == 'select':
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
        if self._chkuser(user):
            # 1) Filter real estates
            real_estates = UserRealEstateSieve(user, self._filters)
            # 2) Select appropriate data
            real_estates = RealEstateDataSelector(
                real_estates, selections=self._includes)
            # 4) Sort real estates
            real_estates = RealEstateSorter(real_estates, self._sort_options)
            # 5) Page result
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
                    # 2) Limit attachments
                    attachments = AttachmentLimiter(
                        attachments,
                        picture_limit=self._picture_limit,
                        floorplan_limit=self._floorplan_limit,
                        document_limit=self._document_limit)
                    # 4) Load attachments
                    attachments = AttachmentLoader(
                        attachments, self.user.max_bytes, self._scaling)
                    # 5) Set manipulated attachments on real estate
                    real_estate.anhaenge.anhang = [a for a in attachments]
                realtor.immobilie.append(real_estate)
            return realtor
        else:
            raise UserNotAllowed(self.cid)

    def _run(self):
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


class AttachmentController(WsgiController):
    """Controller for attachment queries"""

    def _run(self):
        """Returns the queried attachment"""
        ident = self._identifier

    @property
    def _identifier(self):
        """Extracts the customer ID from the query path"""
        if len(self.path) > 1:
            if self.path[1] == 'attachments':
                if len(self.path) == 3:
                    return self.path[2]
                else:
                    raise InvalidPathLength(len(self.path))
            else:
                raise InvalidPathNode(self.path[1])
