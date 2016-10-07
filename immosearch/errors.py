"""Errors of immosearch"""

from homeinfo.lib.wsgi import JSON

__all__ = [
    # <nn>    WSGI top-level errors
    'NoSuchCustomer',
    'InvalidPathLength',
    'InvalidPathNode',
    'InvalidParameterError',
    'UserNotAllowed',
    'OptionAlreadySet',
    'InvalidOptionsCount',
    'NotAnInteger',
    # 1<nn>   Filtering errors
    'NoValidFilterOperation',
    'InvalidFilterOption',
    'FilterOperationNotImplemented',
    'SievingError',
    'SecurityBreach',
    # 2<nn>   Sorting errors
    'InvalidSortingOption',
    # 3<nn>   Scaling errors
    'InvalidRenderingResolution',
    'NoScalingProvided',
    # 5<nn>   Limitation errors
    'HandlersExhausted',
    'MemoryExhausted',
    'InvalidLimiting',
    # 6<nn>   Attachment errors
    'AttachmentNotFound',
    'InvalidAttachmentLimit',
    # 7<nn>   Caching errors
    'Caching',
    'NoDataCached']


class RenderableError(JSON):
    """An error, that can be rendered"""

    def __init__(self, ident, msg, status=400):
        """Sets a unique identifier and a message"""
        error = {}
        error['ident'] = ident
        error['msg'] = msg
        super().__init__(error, status=status)


class NoSuchCustomer(RenderableError):
    """Indicates that an invalid customer has been selected"""

    def __init__(self, cid_str):
        """Initializes error code an message"""
        super().__init__(11, 'No such customer: {0}'.format(cid_str))


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


class AttachmentNotFound(RenderableError):
    """Indicates that the attachment could not be found"""

    def __init__(self):
        """Creates message"""
        super().__init__(601, 'Attachment not found', status=400)


class InvalidAttachmentLimit(RenderableError):
    """Indicates that an invalid attachment limit was provided"""

    def __init__(self, n):
        """Creates message"""
        super().__init__(
            602, 'Invalid attachment limit: {}'.format(n), status=400)


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
