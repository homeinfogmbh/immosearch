"""WSGI-environ interpreter"""

from traceback import format_exc
from peewee import DoesNotExist
from urllib.parse import unquote
from homeinfolib.db import connection
from openimmo import factories
from .lib import Operators
from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, NoValidFilterOperation, InvalidOptionsCount,\
    InvalidRenderingResolution, InvalidPictureLimit, OptionAlreadySet,\
    InvalidOperationError, UserNotAllowed, InvalidAuthenticationOptions,\
    InvalidCredentials, HandlersExhausted, NotAnInteger
from .filter import UserFilter
from .config import core
from .imgscale import AttachmentScaler
from .selector import RealEstateSelector
from .pager import Pager

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['Controller']


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


class Controller():
    """Class that interprets and translates WSGI environment
    variables into a filter, sort and scaling queries
    """

    def __init__(self, path_info, query_string):
        """Initializes the WSGI application with a query string"""
        self._path_info = path_info
        self._query_string = query_string
        self._filters = []
        self._sort_options = []
        self._includes = []
        self._scaling = None
        self._pic_limit = None
        self._auth_token = None
        self._handler_opened = False
        self._limit = None  # Page size limit
        self._page = None
        self._pic_count = None

    def run(self):
        """Main method to call"""
        charset = 'utf-8'
        try:
            response_body = self._run(charset)
        except RenderableError as r:
            status = r.status or '400 Bad Request'
            content_type = 'application/xml'
            response_body = r.render(encoding=charset)
        except:
            status = '500 Internal Server Error'
            content_type = 'text/plain'
            msg = 'Internal Server Error :-('
            if core.get('DEBUG', False):
                msg = '\n'.join([msg, format_exc()])
            response_body = msg.encode(encoding=charset)
        else:
            status = '200 OK'
            content_type = 'application/xml'
        finally:
            if self._handler_opened:
                self.user.current_handlers += -1
        return (status, content_type, charset, response_body)

    @property
    def path_info(self):
        """Returns the path info"""
        return self._path_info

    @property
    def query_string(self):
        """Returns the query string"""
        return self._query_string

    @property
    def queries(self):
        """Returns a list of queries"""
        return self.query_string.split(Separators.QUERY)

    @property
    def cid(self):
        """Extracts the customer ID from the query path"""
        path = [p for p in self.path_info.split(Separators.PATH) if p.strip()]
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

    @property
    def user(self):
        """Returns the user"""
        cid = self.cid
        try:
            with connection(ImmoSearchUser):
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

    def _run(self, encoding):
        """Perform sieving, sorting and rendering"""
        user = self.user
        self.parse()
        if self._chkuser(user):
            # Filter real estates
            immobilie = UserFilter(user, self._filters).filter()
            # Select appropriate data
            selector = RealEstateSelector(immobilie, self._includes,
                                          self._pic_limit, self._pic_count)
            immobilie = selector.immobilie
            # Handle attachments
            scaler = AttachmentScaler(immobilie, self._scaling)
            immobilie = scaler.immobilie
            # immobilie = Sorter(self._sort_options).sort()
            # TODO: Implement sorting
            pager = Pager(immobilie, self._limit)
            immobilie = pager.page(self._page)
            # Generate anbieter
            anbieter = factories.anbieter(str(user.cid),
                                          user.name,
                                          str(user.cid))
            anbieter.immobilie = [i for i in immobilie]
            xml_data = anbieter.toxml(encoding=encoding)
            return xml_data
        else:
            raise UserNotAllowed(self.cid)

    def parse(self):
        """Parses a URI for query commands"""
        for query in self.queries:
            splitted_query = query.split(Separators.ASS)
            if len(splitted_query) >= 2:
                operation = splitted_query[0]
                raw_value = Separators.ASS.join(splitted_query[1:])
                value = unquote(raw_value)
                if operation == Operations.AUTH_TOKEN:
                    self._auth(value)
                elif operation == Operations.INCLUDE:
                    self._include(value)
                elif operation == Operations.FILTER:
                    self._filter(value)
                elif operation == Operations.SORT:
                    self._sort(value)
                elif operation == Operations.ATTACHMENTS:
                    self._attachments(value)
                elif operation == Operations.PAGING:
                    self._paging(value)
                else:
                    raise InvalidOperationError(operation)

    def _auth(self, value):
        """Extract authentication data"""
        if self._auth_token is None:
            auth_opts = value.split(Separators.OPTION)
            if len(auth_opts) != 1:
                raise InvalidAuthenticationOptions()    # Do not propagate data
            else:
                self._auth_token = auth_opts[0]

    def _include(self, value):
        """Select options"""
        includes = value.split(Separators.OPTION)
        for include in includes:
            self._includes.append(include)

    def _filter(self, value):
        """Generate filtering data"""
        option_assignments = value.split(Separators.OPTION)
        for option_assignment in option_assignments:
            operator = None
            for operator_ in Operators():
                split_assignment = option_assignment.split(operator_)
                if len(split_assignment) == 2:
                    option = split_assignment[0]
                    operator = operator_
                    value = split_assignment[1]
                    break
            if operator is None:
                raise NoValidFilterOperation(option_assignment)
            else:
                filter_ = (option, operator, value)
                self._filters.append(filter_)

    def _sort(self, value):
        """Generate filtering data"""
        for sort_option in value.split(Separators.OPTION):
            self._sort_options.append(sort_option)

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
                elif option == 'limit':
                    if self._pic_limit is None:
                        try:
                            limit = int(value)
                        except (ValueError, TypeError):
                            raise InvalidPictureLimit(value)
                        else:
                            self._pic_limit = limit
                    else:
                        raise OptionAlreadySet(option, self._scaling)
                elif option == 'count':
                    if self._pic_count is None:
                        self._pic_count = True
                    else:
                        raise OptionAlreadySet(option, self._scaling)
                else:
                    raise InvalidOperationError(option)

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
                        self._limit = limit
                elif option == 'page':
                    try:
                        page = int(value)
                    except (ValueError, TypeError):
                        raise NotAnInteger(value)
                    else:
                        self._page = page
                else:
                    raise InvalidOperationError(option)
