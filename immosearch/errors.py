"""Errors of immosearch"""

from .error_xml import error

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '27.02.2015'
__all__ = ['InvalidCustomerID', 'InvalidPathLength', 'InvalidPathNode',
           'InvalidOperationError', 'UserNotAllowed', 'OptionAlreadySet',
           'InvalidOptionsCount', 'NotAnInteger', 'InvalidRenderingResolution',
           'NoValidFilterOperation', 'InvalidFilterOption',
           'FilterOperationNotImplemented', 'SievingError',
           'InvalidSortingOption', 'InvalidAuthenticationOptions',
           'InvalidCredentials', 'HandlersExhausted', 'MemoryExhausted']

# Error codes:
# <nn>    WSGI top-level errors
# 1<nn>   Filtering errors
# 2<nn>   Sorting errors
# 3<nn>   Scaling errors
# 4<nn>   Authentication errors
# 5<nn>   Limitation errors


class RenderableError(Exception):
    """An error, that can be rendered"""

    def __init__(self, ident, msg, status=None):
        """Sets a unique identifier and a message"""
        super().__init__(msg)
        self._ident = ident
        self._msg = msg
        self._status = status

    @property
    def status(self):
        """Returns an options HTTP status for override"""
        return self._status

    def toxml(self, encoding='utf-8'):
        """Returns an XML message"""
        result = error()
        result.code = self._ident
        result.msg = self._msg
        return result.toxml(encoding=encoding)


class InvalidCustomerID(RenderableError):
    """Indicates that an invalid customer ID has been specified"""

    def __init__(self, cid_str):
        """Initializes error code an message"""
        super().__init__(11, ' '.join(['Invalid customer ID:', cid_str]))


class InvalidPathLength(RenderableError):
    """Indicates that a query_path with
    an invalid length was provided
    """

    def __init__(self, length):
        """Initializes error code an message"""
        super().__init__(12, ' '.join(['Invalid path length:', str(length)]))


class InvalidPathNode(RenderableError):
    """Indicates that a query_path with
    an invalid node was provided
    """

    def __init__(self, node):
        """Initializes error code an message"""
        super().__init__(13, ' '.join(['Invalid path node:', node]))


class InvalidOperationError(RenderableError):
    """Indicates that an invalid operation was requested"""

    def __init__(self, operation):
        """Initializes error code an message"""
        super().__init__(14, ' '.join(['Invalid operation:', operation]))


class UserNotAllowed(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, cid):
        """Initializes error code an message"""
        super().__init__(15, ' '.join(['User not allowed:', str(cid)]))


class OptionAlreadySet(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, option, value):
        """Initializes error code an message"""
        super().__init__(16, ' '.join(['Option:', option,
                                       'has already been set to:',
                                       str(value)]))


class InvalidOptionsCount(RenderableError):
    """Indicates that not exactly one
    render option was specified"""

    def __init__(self):
        """Initializes error code an message"""
        super().__init__(17, 'Invalid options count')


class NotAnInteger(RenderableError):
    """Indicates that not exactly one
    render option was specified"""

    def __init__(self, i):
        """Initializes error code an message"""
        super().__init__(17, ' '.join(['Not an integer:', str(i)]))


class NoValidFilterOperation(RenderableError):
    """Indicates that no valid operation
    was specified in a filter query"""

    def __init__(self, option_assignment):
        """Initializes error code an message"""
        super().__init__(101, ' '.join(['No valid operation was',
                                        'found in filtering query:',
                                        str(option_assignment)]))


class InvalidFilterOption(RenderableError):
    """Indicates that an invalid filtering
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(102, ' '.join(['Invalid filtering option:',
                                        str(option)]))


class FilterOperationNotImplemented(RenderableError):
    """Indicates that an unimplemented filtering
    operation has been provided
    """

    def __init__(self, operation):
        """Initializes with the faulty option"""
        super().__init__(103, ' '.join(['Invalid filtering operation:',
                                        str(operation)]))


class SievingError(RenderableError):
    """Indicates an error during sieving"""

    def __init__(self, option, operation, value):
        """Sets the option, operation and raw
        value where sieving has gone wrong
        """
        super().__init__(104, ''.join(['Cannot filter real estate by "',
                                       str(option), '" with operation "',
                                       str(operation), '" for value "',
                                       str(value), '"']))


class InvalidSortingOption(RenderableError):
    """Indicates that an invalid sorting
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(201, ' '.join(['Invalid sorting option:',
                                        str(option)]))


class InvalidRenderingResolution(RenderableError):
    """Indicates that an invalid rendering resolution was specified"""

    def __init__(self, resolution):
        """Initializes error code an message"""
        super().__init__(302, ' '.join(['Got invalid rendering resolution:',
                                        resolution,
                                        '- must be like <width>x<height>']))


class NoScalingProvided(RenderableError):
    """Indicates that no scaling resolution was provided"""

    def __init__(self):
        """Initializes error code an message"""
        super().__init__(304, 'No scaling provided')


class InvalidAuthenticationOptions(RenderableError):
    """Indicates that invalid authentication
    options have been provided
    """

    def __init__(self):
        """Initializes error code an message"""
        super().__init__(401, 'Invalid authentication options')


class InvalidCredentials(RenderableError):
    """Indicates that invalid credentials have been suppliedg"""

    def __init__(self):
        """Indicates that invalid credentials have been supplied"""
        super().__init__(402, 'Invalid credentials')


class HandlersExhausted(RenderableError):
    """Indicates that all available event handlers
    for the customer have been exhausted
    """

    def __init__(self, n):
        """Creates message with max. handlers count"""
        h = str(n)
        super().__init__(501, ' '.join(['Handlers exhausted:',
                                        ' / '.join([h, h])]),
                         status=429)


class MemoryExhausted(RenderableError):
    """Indicates that all available memory
    for the customer have been exhausted
    """

    def __init__(self, n):
        """Creates message with memory limit info"""
        b = ' '.join([str(n), 'bytes'])
        super().__init__(502, ' '.join(['Memory limit exhausted:',
                                        ' / '.join([b, b])]),
                         status=413)
