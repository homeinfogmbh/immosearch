"""General API library"""

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['boolean', 'tags', 'Sorting', 'Delims', 'Operators']


boolean = {'true': True,
           'false': False}
"""Boolean string datatype"""


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


class Sorting():
    """Sorting types"""

    ASC = 'ASC'
    DESC = 'DESC'


class Delims():
    """Delimiters"""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ','    # Item separator
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
