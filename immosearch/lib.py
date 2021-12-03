"""General API library"""

from contextlib import suppress
from datetime import datetime
from enum import Enum
from typing import Any, Iterator


__all__ = ['BOOLEAN', 'Operator', 'pdate', 'tags', 'cast']


BOOLEAN = {'true': True, 'false': False}


class Delim(Enum):
    """Delimiters."""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ';'    # Item separator
    BEGIN_INDEX = '['
    END_INDEX = ']'


class Operator(Enum):
    """Filtering operators."""

    EQ = '=='   # Equals
    EG = '~='   # Equals glob
    EC = '%='   # Equals case-insensitive
    NE = '!='   # Does not equal
    NG = '!~'   # Does not glob
    NC = '!%'   # Does not equal case-insensitive
    LT = '<'    # Less-than
    LE = '<='   # Less-than or equal
    GT = '>'    # Greater-than
    GE = '>='   # Greater-than or equal
    IN = '∈'    # Element in iterable
    NI = '∉'    # Element not in iterable
    CO = '∋'    # List contains element
    CN = '∌'    # List does not contain element


def pdate(string: str) -> datetime:
    """Parse a datetime string."""

    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')


def tags(template: str, tag_open: str = '<%',
         tag_close: str = '%>') -> Iterator[str]:
    """Yields tags found in a template."""

    record = False
    window = ''
    token = tag_open
    tag = ''

    for char in template:
        # Records tag content iff in record mode
        if record:
            tag += char

        # Increase window size
        if len(window) < len(token):
            window += char
        else:   # Move window
            window = window[1:len(token)] + char

        # Check for opening tag
        if not record and window == tag_open:
            # Reset window, record and token
            record = True
            window = ''
            token = tag_close

        # Check for closing tag
        elif record and window == tag_close:
            # Remove current window from end of tag
            tag_content = tag[:-len(window)]

            # Reset window, record, token and tag
            window = ''
            record = False
            token = tag_open
            tag = ''

            yield tag_content


def cast(value: str, typ: type = None) -> Any:  # pylint: disable=R0911
    """Type cast a raw string value for a certain type
    XXX: Nested lists are not supported, yet.
    """
    if typ is not None:
        return typ(value)

    if value.startswith(Delim.SL.value):
        if value.endswith(Delim.EL.value):
            return [
                cast(elem.strip()) for elem in
                value[1:-1].split(Delim.IS.value)
            ]

    with suppress(ValueError):
        return int(value)

    with suppress(ValueError):
        return float(value)

    with suppress(KeyError):
        return BOOLEAN[value.lower()]

    with suppress(ValueError):
        return pdate(value)

    return value
