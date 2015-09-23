"""General API library"""

from datetime import datetime

__all__ = ['boolean', 'debug', 'pdate', 'tags', 'cast',
           'Sorting', 'Delims', 'Operators', 'RealEstate']


boolean = {
    'true': True,
    'false': False
    }


def debug(s, d=None):
    """Write debug data"""
    msg = ''.join([str(datetime.now()), '\t',
                   str(s) if d is None else '\t'.join([d, str(s)]), '\n'])
    with open('/tmp/auth.txt', 'a') as f:
        f.write(msg)


def pdate(date_str):
    """Parse a datetime string"""
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')


def tags(template, tag_open='<%', tag_close='%>'):
    """Yields tags found in a template"""
    record = False
    window = ''
    token = tag_open
    tag = ''
    for c in template:
        # Records tag content iff in record mode
        if record:
            tag += c
        # Increase window size
        if len(window) < len(token):
            window += c
        else:   # Move window
            window = window[1:len(token)] + c
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


def cast(val, typ=None):
    """Type cast a raw string value for a certain type
    XXX: Nested lists are not supported, yet
    """
    if typ is None:  # Cast intelligent
        # Check for list
        if val.startswith(Delims.SL) and val.endswith(Delims.EL):
            return [cast(elem.strip()) for elem in val[1:-1].split(Delims.IS)]
        else:
            # Check for integer
            try:
                i = int(val)
            except ValueError:
                # Check for float
                try:
                    f = float(val)
                except ValueError:
                    # Check for boolean
                    b = boolean.get(val.lower())
                    if b is not None:
                        return b
                    else:
                        # Try to parse a date string
                        try:
                            d = pdate(val)
                        # Return raw string if nothing else fits
                        except ValueError:
                            return val
                        else:
                            return d
                else:
                    return f
            else:
                return i
    else:
        return typ(val)  # Cast with specified constructor method


class Sorting():
    """Sorting types"""

    ASC = 'ASC'
    DESC = 'DESC'


class Delims():
    """Delimiters"""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ';'    # Item separator
    BEGIN_INDEX = '['
    END_INDEX = ']'


class Operators():
    """Filtering operators"""

    EQ = '=='   # Equals
    EG = '~='   # Equals glob
    EC = '%='   # Equals case-insensitive
    NE = '!='   # Does not equal
    NG = '!~'   # Does not glob
    NC = '!%'   # Does not equal case-insensitive
    LT = '<<'   # Less-than
    LE = '<='   # Less-than or equal
    GT = '>>'   # Greater-than
    GE = '>='   # Greater-than or equal
    IN = '∈'    # Element in iterable
    NI = '∉'    # Element not in iterable
    CO = '∋'    # List contains element
    CN = '∌'    # List does not contain element

    def __iter__(self):
        """Iterates over the operators"""
        for attr in dir(self):
            if (attr.upper() == attr) and (len(attr) == 2):
                yield getattr(self, attr)


class RealEstate():
    """Real estate ORM / DOM wrapper"""

    def __init__(self, immobilie_orm):
        """Creates the real estate from a database record"""
        self._orm = immobilie_orm
        self._dom = None

    @property
    def orm(self):
        return self._orm

    @property
    def dom(self):
        if self._dom is None:
            self._dom = self._orm.dom
        return self._dom
