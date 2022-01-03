"""General API library"""

from contextlib import suppress
from datetime import datetime
from enum import Enum
from typing import Any


__all__ = ['BOOLEAN', 'Operator', 'cast']


BOOLEAN = {
    'true'.casefold(): True,
    'false'.casefold(): False
}


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


def cast(value: str, typ: type = None) -> Any:  # pylint: disable=R0911
    """Type cast a raw string value for a certain type
    XXX: Nested lists are not supported, yet.
    """
    if typ is not None:
        return typ(value)

    if value.startswith(Delim.SL.value) and value.endswith(Delim.EL.value):
        return [cast(e.strip()) for e in value[1:-1].split(Delim.IS.value)]

    with suppress(ValueError):
        return int(value)

    with suppress(ValueError):
        return float(value)

    with suppress(KeyError):
        return BOOLEAN[value.casefold()]

    with suppress(ValueError):
        return datetime.fromisoformat(value)

    return value
