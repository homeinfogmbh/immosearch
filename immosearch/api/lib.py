"""Filtering library"""

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['Delims', 'Operators']


class Delims():
    """Filtering delimiters"""

    SL = '['    # Start list
    EL = ']'    # End list
    IS = ','    # Item separator


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
