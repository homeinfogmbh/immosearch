"""Errors of immosearch"""

from wsgilib import JSON

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
        super().__init__(11, 'No such customer: {}'.format(cid_str))


class InvalidPathLength(RenderableError):
    """Indicates that a query_path with
    an invalid length was provided
    """

    def __init__(self, length):
        """Initializes error code an message"""
        super().__init__(12, 'Invalid path length: {}'.format(length))


class InvalidPathNode(RenderableError):
    """Indicates that a query_path with
    an invalid node was provided
    """

    def __init__(self, node):
        """Initializes error code an message"""
        super().__init__(13, 'Invalid path node: {}'.format(node))


class InvalidParameterError(RenderableError):
    """Indicates that an invalid operation was requested"""

    def __init__(self, operation):
        """Initializes error code an message"""
        super().__init__(14, 'Invalid parameter: {}'.format(operation))


class UserNotAllowed(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, cid):
        """Initializes error code an message"""
        super().__init__(15, 'User not allowed: {}'.format(cid))


class OptionAlreadySet(RenderableError):
    """Indicates that a user is not allowed to use immosearch"""

    def __init__(self, option, value):
        """Initializes error code an message"""
        super().__init__(
            16, 'Option "{}" has already been set to: {}'.format(
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

    def __init__(self, integer):
        """Initializes error code an message"""
        super().__init__(18, 'Not an integer: {}'.format(integer))


class NoValidFilterOperation(RenderableError):
    """Indicates that no valid operation
    was specified in a filter query"""

    def __init__(self, option_assignment):
        """Initializes error code an message"""
        super().__init__(
            101, 'No valid operation was found in filtering query: {}'.format(
                option_assignment))


class InvalidFilterOption(RenderableError):
    """Indicates that an invalid filtering
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(102, 'Invalid filtering option: {}'.format(option))


class FilterOperationNotImplemented(RenderableError):
    """Indicates that an unimplemented filtering
    operation has been provided
    """

    def __init__(self, operation):
        """Initializes with the faulty option"""
        super().__init__(
            103, 'Invalid filtering operation: {}'.format(operation))


class SievingError(RenderableError):
    """Indicates an error during sieving"""

    def __init__(self, option, operation, value):
        """Sets the option, operation and raw
        value where sieving has gone wrong
        """
        super().__init__(
            104, 'Cannot filter real estate by "{}" with operation "{}" '
            'for value "{}"'.format(option, operation, value))


class SecurityBreach(RenderableError):
    """Indicates errors during boolean parser's security checks"""

    def __init__(self, msg):
        super().__init__(
            105, 'Caught security error while parsing the search filter: '
            '{}'.format(msg))


class InvalidSortingOption(RenderableError):
    """Indicates that an invalid sorting
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(201, 'Invalid sorting option: {}'.format(option))


class InvalidRenderingResolution(RenderableError):
    """Indicates that an invalid rendering resolution was specified"""

    def __init__(self, resolution):
        """Initializes error code an message"""
        super().__init__(
            302, 'Got invalid rendering resolution: {} - must be like '
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

    def __init__(self, number):
        """Creates message with max. handlers count"""
        super().__init__(
            501, 'Handlers exhausted: {0}/{0}'.format(number), status=429)


class MemoryExhausted(RenderableError):
    """Indicates that all available memory
    for the customer have been exhausted
    """

    def __init__(self, number):
        """Creates message with memory limit info"""
        bytes_str = '{} bytes'.format(number)
        super().__init__(
            502, 'Memory limit exhausted: {0}/{0}'.format(bytes_str),
            status=413)


class InvalidLimiting(RenderableError):
    """Indicates that an invalid limiting has been requested"""

    def __init__(self, msg):
        """Creates message with memory limit info"""
        super().__init__(503, 'Invalid limiting: {}'.format(msg), status=400)


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
            702, 'No data cached for user "{}"'.format(cid), status=500)
