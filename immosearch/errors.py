"""Errors of immosearch"""

from homeinfo.lib.wsgi import XML

from .dom import error

__all__ = [
    'InvalidCustomerID', 'InvalidPathLength', 'InvalidPathNode',
    'InvalidParameterError', 'UserNotAllowed', 'OptionAlreadySet',
    'InvalidOptionsCount', 'NotAnInteger', 'InvalidRenderingResolution',
    'NoValidFilterOperation', 'InvalidFilterOption',
    'FilterOperationNotImplemented', 'SievingError', 'SecurityBreach'
    'InvalidSortingOption', 'InvalidAuthenticationOptions',
    'InvalidCredentials', 'HandlersExhausted', 'MemoryExhausted',
    'InvalidLimiting', 'MissingIdentifier', 'Caching', 'NoDataCached']

# Error codes:
# <nn>    WSGI top-level errors
# 1<nn>   Filtering errors
# 2<nn>   Sorting errors
# 3<nn>   Scaling errors
# 4<nn>   Authentication errors
# 5<nn>   Limitation errors
# 6<nn>   Attachment errors
# 7<nn>   Caching errors


class RenderableError(XML):
    """An error, that can be rendered"""

    def __init__(self, ident, msg, status=None):
        """Sets a unique identifier and a message"""
        self.ident = ident
        self.msg = msg
        self.status = status
        super().__init__(self.dom)

    @property
    def dom(self):
        """Returns an XML message"""
        result = error()
        result.code = self.ident
        result.msg = self.msg
        return result


class InvalidCustomerID(RenderableError):
    """Indicates that an invalid customer ID has been specified"""

    def __init__(self, cid_str):
        """Initializes error code an message"""
        super().__init__(11, 'Invalid customer ID: {0}'.format(cid_str))


class InvalidPathLength(RenderableError):
    """Indicates that a query_path with
    an invalid length was provided
    """

    def __init__(self, length):
        """Initializes error code an message"""
        super().__init__(12, 'Invalid path length: {0}'.format(length))


class InvalidPathNode(RenderableError):
    """Indicates that a query_path with
    an invalid node was provided
    """

    def __init__(self, node):
        """Initializes error code an message"""
        super().__init__(13, 'Invalid path node: {0}'.format(node))


class InvalidParameterError(RenderableError):
    """Indicates that an invalid operation was requested"""

    def __init__(self, operation):
        """Initializes error code an message"""
        super().__init__(14, 'Invalid parameter: {0}'.format(operation))


class UserNotAllowed(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, cid):
        """Initializes error code an message"""
        super().__init__(15, 'User not allowed: {0}'.format(cid))


class OptionAlreadySet(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, option, value):
        """Initializes error code an message"""
        super().__init__(
            16, 'Option "{0}" has already been set to: {1}'.format(
                option, value))


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
        super().__init__(18, 'Not an integer: {0}'.format(i))


class NoValidFilterOperation(RenderableError):
    """Indicates that no valid operation
    was specified in a filter query"""

    def __init__(self, option_assignment):
        """Initializes error code an message"""
        super().__init__(
            101, 'No valid operation was found in filtering query: {0}'.format(
                option_assignment))


class InvalidFilterOption(RenderableError):
    """Indicates that an invalid filtering
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(102, 'Invalid filtering option: {0}'.format(option))


class FilterOperationNotImplemented(RenderableError):
    """Indicates that an unimplemented filtering
    operation has been provided
    """

    def __init__(self, operation):
        """Initializes with the faulty option"""
        super().__init__(
            103, 'Invalid filtering operation: {0}'.format(operation))


class SievingError(RenderableError):
    """Indicates an error during sieving"""

    def __init__(self, option, operation, value):
        """Sets the option, operation and raw
        value where sieving has gone wrong
        """
        super().__init__(
            104, 'Cannot filter real estate by "{0}" with operation "{1}" '
            'for value "{2}"'.format(option, operation, value))


class SecurityBreach(RenderableError):
    """Indicates errors during boolean parser's security checks"""

    def __init__(self, msg):
        super().__init__(
            105, 'Caught security error while parsing the search filter: '
            '{0}'.format(msg))


class InvalidSortingOption(RenderableError):
    """Indicates that an invalid sorting
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(201, 'Invalid sorting option: {0}'.format(option))


class InvalidRenderingResolution(RenderableError):
    """Indicates that an invalid rendering resolution was specified"""

    def __init__(self, resolution):
        """Initializes error code an message"""
        super().__init__(
            302, 'Got invalid rendering resolution: {0} - must be like '
            '<width>x<height>'.format(resolution))


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
        super().__init__(
            501, 'Handlers exhausted: {0}/{0}'.format(h), status=429)


class MemoryExhausted(RenderableError):
    """Indicates that all available memory
    for the customer have been exhausted
    """

    def __init__(self, n):
        """Creates message with memory limit info"""
        b = ' '.join([str(n), 'bytes'])
        super().__init__(
            502, 'Memory limit exhausted: {0}/{0}'.format(b), status=413)


class InvalidLimiting(RenderableError):
    """Indicates that an invalid limiting has been requested"""

    def __init__(self, msg):
        """Creates message with memory limit info"""
        super().__init__(503, 'Invalid limiting: {0}'.format(msg), status=400)


class MissingIdentifier(RenderableError):
    """Indicates that no identifier was
    provided on an attachment request
    """

    def __init__(self):
        """Creates message"""
        super().__init__(601, 'Missing identifier', status=400)


class InvalidAttachmentLimit(RenderableError):
    """Indicates that an invalid attachment limit has been provided"""

    def __init__(self, limit):
        """Creates message"""
        super().__init__(
            602, 'Invalid attachment limit: {0}'.format(limit), status=400)


class Caching(RenderableError):
    """Indicates that the server is currently (re-)caching data"""

    def __init__(self):
        """Creates message"""
        super().__init__(
            701, 'Server is currently caching data - please be patient',
            status=500)


class NoDataCached(RenderableError):
    """Indicates that no data has been cached for the respective user"""

    def __init__(self, cid):
        """Creates message"""
        super().__init__(
            702, 'No data cached for user "{0}"'.format(cid), status=500)
