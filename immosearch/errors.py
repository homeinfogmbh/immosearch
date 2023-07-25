"""Errors of immosearch."""

from typing import Any

from wsgilib import JSON


__all__ = [
    # <nn>    WSGI top-level errors
    "NoSuchCustomer",
    "InvalidParameterError",
    "UserNotAllowed",
    "OptionAlreadySet",
    "InvalidOptionsCount",
    "NotAnInteger",
    # 1<nn>   Filtering errors
    "InvalidFilterOption",
    "SievingError",
    "SecurityBreach",
    # 2<nn>   Sorting errors
    "InvalidSortingOption",
    # 3<nn>   Scaling errors
    "InvalidRenderingResolution",
    "NoScalingProvided",
    # 5<nn>   Limitation errors
    "HandlersExhausted",
    "MemoryExhausted",
    "InvalidLimiting",
    # 6<nn>   Attachment errors
    "AttachmentNotFound",
    "InvalidAttachmentLimit",
    # 7<nn>   Caching errors
    "Caching",
    "NoDataCached",
]


class RenderableError(JSON):
    """An error, that can be rendered."""

    def __init__(self, ident: int, msg: str, status: int = 400):
        """Sets a unique identifier and a message."""
        error = {}
        error["ident"] = ident
        error["msg"] = msg
        super().__init__(error, status=status)


class NoSuchCustomer(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid customer has been selected."""

    def __init__(self, cid_str: str):
        """Initializes error code an message"""
        super().__init__(11, f"No such customer: {cid_str}.")


class InvalidParameterError(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid operation was requested."""

    def __init__(self, operation: str):
        """Initializes error code an message."""
        super().__init__(14, f"Invalid parameter: {operation}.")


class UserNotAllowed(RenderableError):  # pylint: disable=R0901
    """Indicates that a user is not allowed to use immosearch."""

    def __init__(self, cid: int):
        """Initializes error code an message."""
        super().__init__(15, f"User not allowed: {cid}.")


class OptionAlreadySet(RenderableError):  # pylint: disable=R0901
    """Indicates that a user is not allowed to use immosearch."""

    def __init__(self, option: str, value: str):
        """Initializes error code an message."""
        super().__init__(16, f'Option "{option}" has already been set to: {value}.')


class InvalidOptionsCount(RenderableError):  # pylint: disable=R0901
    """Indicates that not exactly one
    render option was specified.
    """

    def __init__(self):
        """Initializes error code an message."""
        super().__init__(17, "Invalid options count.")


class NotAnInteger(RenderableError):  # pylint: disable=R0901
    """Indicates that not exactly one
    render option was specified.
    """

    def __init__(self, not_integer: Any):
        """Initializes error code an message."""
        super().__init__(18, f"Not an integer: {not_integer}.")


class InvalidFilterOption(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid filtering
    option has been provided.
    """

    def __init__(self, option):
        """Initializes with the faulty option."""
        super().__init__(102, f"Invalid filtering option: {option}.")


class SievingError(RenderableError):  # pylint: disable=R0901
    """Indicates an error during sieving."""

    def __init__(self, option, operation, value):
        """Sets the option, operation and raw
        value where sieving has gone wrong.
        """
        super().__init__(
            104,
            f'Cannot filter real estate by "{option}" with operation '
            f'"{operation}" for value "{value}".',
        )


class SecurityBreach(RenderableError):  # pylint: disable=R0901
    """Indicates errors during boolean parser's security checks."""

    def __init__(self, msg):
        super().__init__(
            105, "Caught security error while parsing the search filter: " f"{msg}."
        )


class InvalidSortingOption(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid sorting
    option has been provided.
    """

    def __init__(self, option):
        """Initializes with the faulty option."""
        super().__init__(201, f"Invalid sorting option: {option}.")


class InvalidRenderingResolution(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid rendering resolution was specified."""

    def __init__(self, resolution):
        """Initializes error code an message."""
        super().__init__(
            302,
            f"Got invalid rendering resolution: {resolution} - "
            "must be like <width>x<height>.",
        )


class NoScalingProvided(RenderableError):  # pylint: disable=R0901
    """Indicates that no scaling resolution was provided."""

    def __init__(self):
        """Initializes error code an message."""
        super().__init__(304, "No scaling provided.")


class HandlersExhausted(RenderableError):  # pylint: disable=R0901
    """Indicates that all available event handlers
    for the customer have been exhausted.
    """

    def __init__(self, number):
        """Creates message with max. handlers count."""
        super().__init__(501, f"Handlers exhausted: {number}/{number}.", status=429)


class MemoryExhausted(RenderableError):  # pylint: disable=R0901
    """Indicates that all available memory
    for the customer have been exhausted.
    """

    def __init__(self, number):
        """Creates message with memory limit info."""
        super().__init__(
            502, f"Memory limit exhausted: {number} bytes/{number} bytes.", status=413
        )


class InvalidLimiting(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid limiting has been requested."""

    def __init__(self, msg):
        """Creates message with memory limit info."""
        super().__init__(503, f"Invalid limiting: {msg}.", status=400)


class AttachmentNotFound(RenderableError):  # pylint: disable=R0901
    """Indicates that the attachment could not be found."""

    def __init__(self):
        """Creates message."""
        super().__init__(601, "Attachment not found.", status=400)


class InvalidAttachmentLimit(RenderableError):  # pylint: disable=R0901
    """Indicates that an invalid attachment limit was provided."""

    def __init__(self, n):
        """Creates message."""
        super().__init__(602, f"Invalid attachment limit: {n}.", status=400)


class Caching(RenderableError):  # pylint: disable=R0901
    """Indicates that the server is currently (re-)caching data."""

    def __init__(self):
        """Creates message."""
        super().__init__(
            701, "Server is currently caching data - please be patient.", status=500
        )


class NoDataCached(RenderableError):  # pylint: disable=R0901
    """Indicates that no data has been cached for the respective user."""

    def __init__(self, cid):
        """Creates message."""
        super().__init__(702, f'No data cached for user "{cid}".', status=500)
