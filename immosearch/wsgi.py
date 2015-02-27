"""WSGI-environ interpreter"""

from peewee import DoesNotExist
from .lib import Operators
from .db import ImmoSearchUser
from .errors import InvalidCustomerID, InvalidPathLength, InvalidPathNode,\
    NoValidFilterOperation, InvalidRenderingOptionsCount, \
    InvalidRenderingResolution, RenderingOptionsAlreadySet

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['WSGIEnvInterpreter']


class Separators():
    """Special separation characters"""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = '%'
    PATH = '/'


class Operations():
    """Valid query operations"""

    FILTER = 'filter'
    SORT = 'sort'
    RENDER = 'render'


class PathNodes():
    """Valid path nodes"""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


class WSGIEnvInterpreter():
    """Class that interprets and translates WSGI
    environment variables into a filter query
    """

    def __init__(self, path_info, query_string):
        """Initializes the WSGI application with a query string"""
        self._path_info = path_info
        self._query_string = query_string
        self._filters = []
        self._sort_options = []
        self._rendering = None

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
            if path[1] == PathNodes.OPENIMMO:
                pass    # TODO: Implement
            elif path[1] == PathNodes.CUSTOMER:
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
            user = ImmoSearchUser.get(self.cid)
        except DoesNotExist:
            return None
        else:
            return user

    def run(self):
        """Perform sieving, sorting and rendering"""
        self.chkuser()
        self.parse()

    def chkuser(self):
        """Check whether user is allowed to retrieve real estates"""
        pass    # TODO: Implement

    def parse(self):
        """Parses a URI for query commands"""
        for query in self.queries:
            splitted_query = query.split(Separators.ASS)
            if len(splitted_query) >= 2:
                operation = splitted_query[0]
                value = Separators.ASS.join(splitted_query[1:])
                if operation == Operations.FILTER:
                    self._filter(value)
                elif operation == Operations.SORT:
                    self._sort(value)
                elif operation == Operations.RENDER:
                    self._render(value)
                else:
                    pass    # TODO: raise Exception

    def _filter(self, value):
        """Generate filtering data"""
        option_assignments = value.split(Separators.OPTION)
        for option_assignment in option_assignments:
            operator = None
            for operator_ in Operators:
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

    def _render(self, value):
        """Generate filtering data"""
        if self._rendering is None:
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
                        self._rendering = (x, y)
        else:
            raise RenderingOptionsAlreadySet(self._rendering)
