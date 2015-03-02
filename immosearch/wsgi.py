"""WSGI-environ interpreter"""

from traceback import format_exc
from peewee import DoesNotExist
from contextlib import suppress
from urllib.parse import unquote
from tempfile import NamedTemporaryFile
from homeinfolib.db import connection
from openimmo import factories
from .lib import Operators
from .db import ImmoSearchUser
from .errors import RenderableError, InvalidCustomerID, InvalidPathLength,\
    InvalidPathNode, NoValidFilterOperation, InvalidRenderingOptionsCount,\
    InvalidRenderingResolution, RenderingOptionsAlreadySet,\
    InvalidOperationError, UserNotAllowed, InvalidAuthenticationOptions,\
    InvalidCredentials, HandlersExhausted
from .filter import UserFilter
from .config import core
from .imgscale import AttachmentScaler
from .lib import debug
from immosearch.selector import RealEstateSelector

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['Controller']


class Separators():
    """Special separation characters"""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = '%'
    PATH = '/'


class Operations():
    """Valid query operations"""

    SELECT = 'select'
    FILTER = 'filter'
    SORT = 'sort'
    SCALING = 'scale'
    AUTH_TOKEN = 'auth_token'


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
        self._select_opts = []
        self._scaling = None
        self._rendering = None
        self._auth_token = None
        self._handler_opened = False

    def run(self):
        """Main method to call"""
        charset = 'UTF-8'
        try:
            response_body = self._run(charset)
        except RenderableError as r:
            status = '400 Bad Request'
            charset = 'UTF-8'
            content_type = 'application/xml'
            response_body = r.render(encoding=charset)
        except:
            status = '500 Internal Server Error'
            charset = 'UTF-8'
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
        return (status, response_body, content_type, charset)

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
        try:
            with connection(ImmoSearchUser):
                user = ImmoSearchUser.get(ImmoSearchUser.customer == self.cid)
        except DoesNotExist:
            return None
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
            if self._select_opts:
                selector = RealEstateSelector(immobilie, self._select_opts)
                immobilie = selector.immobilie
            # Render attachments
            if self._rendering:
                scaler = AttachmentScaler(immobilie, self._rendering)
                immobilie = scaler.immobilie
            # immobilie = Sorter(self._sort_options).sort()
            # TODO: Implement sorting
            # Generate anbieter
            anbieter = factories.anbieter(str(user.customer.id),
                                          user.customer.name,
                                          str(user.customer.id))
            anbieter.immobilie = [i for i in immobilie]
            xml_data = anbieter.toxml(encoding=encoding)
            return xml_data
        else:
            raise UserNotAllowed(self.cid)

    def parse(self):
        """Parses a URI for query commands"""
        for query in self.queries:
            debug(query, 'query')
            splitted_query = query.split(Separators.ASS)
            if len(splitted_query) >= 2:
                operation = splitted_query[0]
                raw_value = Separators.ASS.join(splitted_query[1:])
                debug(operation, 'operation')
                debug(raw_value, 'raw_value')
                value = unquote(raw_value)
                if operation == Operations.SELECT:
                    self._select(value)
                elif operation == Operations.FILTER:
                    self._filter(value)
                elif operation == Operations.SORT:
                    self._sort(value)
                elif operation == Operations.SCALING:
                    self._scale(value)
                elif operation == Operations.AUTH_TOKEN:
                    self._auth(value)
                else:
                    raise InvalidOperationError(operation)

    def _select(self, value):
        """Select options"""
        select_opts = value.split(Separators.OPTION)
        for select_opt in select_opts:
            self._select_opts.append(select_opt)

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

    def _scale(self, value):
        """Generate scaling data"""
        if self._scaling is None:
            render_opts = value.split(Separators.OPTION)
            if len(render_opts) != 1:
                raise InvalidRenderingOptionsCount()
            else:
                render_opt = render_opts[0]
                try:
                    str_x, str_y = render_opt.split('x')
                except ValueError:
                    raise InvalidRenderingResolution(render_opt)
                else:
                    try:
                        x = int(str_x)
                        y = int(str_y)
                    except:
                        raise InvalidRenderingResolution(render_opt)
                    else:
                        self._scaling = (x, y)
        else:
            raise RenderingOptionsAlreadySet(self._scaling)

    def _auth(self, value):
        """Extract authentication data"""
        if self._auth_token is None:
            debug(value, 'value')
            auth_opts = value.split(Separators.OPTION)
            if len(auth_opts) != 1:
                raise InvalidAuthenticationOptions()    # Do not propagate data
            else:
                self._auth_token = auth_opts[0]
                debug(auth_opts, 'auth_opts')
