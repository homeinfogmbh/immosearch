"""WSGI-environ interpreter"""

from .lib import Operators

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['WSGIEnvInterpreter']


class InvalidRenderingOptionsCount(Exception):
    """Indicates that not exactly one
    render option was specified"""

    def __init__(self, n):
        """Sets the message"""
        super().__init__(' '.join(['Need exactly one rendering option, but',
                                   str(n), 'where given']))


class InvalidRenderingResolution(Exception):
    """Indicates that an invalid rendering resolution was specified"""

    def __init__(self, resolution):
        """Sets the message"""
        super().__init__(' '.join(['Got invalid rendering resolution:',
                                   resolution,
                                   '- must be like <width>x<heigth>']))


class RenderingOptionsAlreadySet(Exception):
    """Indicates that rendering options have already been set"""

    def __init__(self, resolution):
        """Sets the message"""
        super().__init__(' '.join(['Rendering resolution has',
                                   'already been set to:',
                                   'x'.join([str(n) for n in resolution])]))


class NoValidOperationSpecified(Exception):
    """Indicates that no valid operation
    was specified in a filter query"""

    def __init__(self, option_assignment):
        """Sets the message"""
        super().__init__(' '.join(['No valid operation was',
                                   'found in filter query:',
                                   str(option_assignment)]))


class Separators():
    """Special separation characters"""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = '%'


class Operations():
    """Valid query operations"""

    FILTER = 'filter'
    SORT = 'sort'
    RENDER = 'render'


class WSGIEnvInterpreter():
    """Class that interprets and translates WSGI
    environment variables into a filter query
    """

    def __init__(self, query_string):
        """Initializes the WSGI application with a query string"""
        self._query_string = query_string
        self._filters = []
        self._sort_options = []
        self._rendering = None

    @property
    def query_string(self):
        """Returns the query string"""
        return self._query_string

    @property
    def queries(self):
        """Returns a list of queries"""
        return self.query_string.split(Separators.QUERY)

    def run(self):
        """Perform sieving, sorting and rendering"""
        

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
                raise NoValidOperationSpecified(option_assignment)
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
