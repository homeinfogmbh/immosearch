"""General API library"""

from enum import Enum

from datetime import datetime

__all__ = [
    'BOOLEAN',
    'pdate',
    'tags',
    'cast',
    'Delims',
    'Operators']


BOOLEAN = {
    'true': True,
    'false': False}


def pdate(date_str):
    """Parse a datetime string."""
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')


def tags(template, tag_open='<%', tag_close='%>'):
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


def cast(value, typ=None):
    """Type cast a raw string value for a certain type
    XXX: Nested lists are not supported, yet.
    """
    if typ is None:
        if value.startswith(Delims.SL.value):
            if value.endswith(Delims.EL.value):
                return [
                    cast(elem.strip()) for elem in
                    value[1:-1].split(Delims.IS.value)]

        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                try:
                    return BOOLEAN[value.lower()]
                except KeyError:
                    try:
                        return pdate(value)
                    except ValueError:
                        return value

    return typ(value)


class Delims(Enum):
    """Delimiters."""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ';'    # Item separator
    BEGIN_INDEX = '['
    END_INDEX = ']'


class Operators(Enum):
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
