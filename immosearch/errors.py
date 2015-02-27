"""Errors of immosearch"""

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '27.02.2015'
__all__ = ['InvalidCustomerID', 'InvalidPathLength', 'InvalidPathNode',
           'InvalidRenderingOptionsCount', 'InvalidRenderingResolution',
           'RenderingOptionsAlreadySet', 'NoValidFilterOperation',
           'InvalidFilterOption', 'FilterOperationNotImplemented',
           'SievingError']


class RenderableError(Exception):
    """An error, that can be rendered"""

    def __init__(self, ident, msg):
        """Sets a unique identifier and a message"""
        super().__init__(msg)
        self._ident = ident
        self._msg = msg

    @property
    def ident(self):
        """Returns the ID"""
        return self._ident

    @property
    def msg(self):
        """Returns the message"""
        return self._msg

    def render(self):
        """Returns a tuple of ID and message"""
        return (self.ident, self.msg)


class InvalidCustomerID(RenderableError):
    """Indicates that an invalid customer ID has been specified"""

    def __init__(self, cid_str):
        """Sets the message"""
        super().__init__(11, ' '.join(['Invalid customer ID:', cid_str]))


class InvalidPathLength(RenderableError):
    """Indicates that a query_path with
    an invalid length was provided
    """

    def __init__(self, length):
        """Sets the message"""
        super().__init__(12, ' '.join(['Invalid path length:', str(length)]))


class InvalidPathNode(RenderableError):
    """Indicates that a query_path with
    an invalid node was provided
    """

    def __init__(self, node):
        """Sets the message"""
        super().__init__(13, ' '.join(['Invalid path length:', node]))


class InvalidRenderingOptionsCount(RenderableError):
    """Indicates that not exactly one
    render option was specified"""

    def __init__(self, n):
        """Sets the message"""
        super().__init__(301, ' '.join(['Need exactly one rendering option,',
                                        'but', str(n), 'where given']))


class InvalidRenderingResolution(RenderableError):
    """Indicates that an invalid rendering resolution was specified"""

    def __init__(self, resolution):
        """Sets the message"""
        super().__init__(302, ' '.join(['Got invalid rendering resolution:',
                                        resolution,
                                        '- must be like <width>x<heigth>']))


class RenderingOptionsAlreadySet(RenderableError):
    """Indicates that rendering options have already been set"""

    def __init__(self, resolution):
        """Sets the message"""
        super().__init__(303, ' '.join(['Rendering resolution has',
                                        'already been set to:',
                                        'x'.join([str(n) for n in
                                                  resolution])]))


class NoValidFilterOperation(RenderableError):
    """Indicates that no valid operation
    was specified in a filter query"""

    def __init__(self, option_assignment):
        """Sets the message"""
        super().__init__(101, ' '.join(['No valid operation was',
                                        'found in filter query:',
                                        str(option_assignment)]))


class InvalidFilterOption(RenderableError):
    """Indicates that an invalid filtering
    option has been provided
    """

    def __init__(self, option):
        """Initializes with the faulty option"""
        super().__init__(102, ' '.join(['Invalid filtering option:',
                                        str(option)]))
        self._option = option

    @property
    def option(self):
        """Returns the faulty option"""
        return self._option


class FilterOperationNotImplemented(RenderableError):
    """Indicates that an unimplemented filtering
    operation has been provided
    """

    def __init__(self, operation):
        """Initializes with the faulty option"""
        super().__init__(103, ' '.join(['Invalid filtering operation:',
                                        str(operation)]))
        self._operation = operation

    @property
    def operation(self):
        """Returns the faulty operation"""
        return self._operation


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
        self._option = option
        self._operation = operation
        self._value = value

    @property
    def option(self):
        """Returns the sieving option"""
        return self._option

    @property
    def operation(self):
        """Returns the sieving operation"""
        return self._operation

    @property
    def value(self):
        """Returns the sieving value"""
        return self._value
