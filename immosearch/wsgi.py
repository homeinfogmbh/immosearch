"""WSGI-environ interpreter"""

from .query import OpenImmoQuery

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['WSGIEnvInterpreter']


class Separators():
    """Special separation characters"""

    PATH = '/'
    REQ = '?'
    PARAM = '&'
    ASS = '='
    LIST = ','
    ATTR = '%'


class WSGIEnvInterpreter():
    """Class that interprets and translates WSGI
    environment variables into a filter query
    """

    def parse(self, query_string):
        """Parses a URI for query commands"""
        params = query_string.split(Separators.PARAM)
        filters = {}
        sorts = {}
        paging = None
        page = None
        raw = False
        for p in params:
            param_path = p.split(Separators.ASS)
            pname = param_path[0]
            pval = param_path[1]
            if pname == 'filter':
                node, values_, inverted_ = pval.split(Separators.ATTR)
                values = values_.split(Separators.LIST)
                inverted = self._bool(inverted_)
                filters[node] = (values, inverted)
            elif pname == 'sort':
                node, inverted_ = pval.split(Separators.ATTR)
                inverted = self._bool(inverted_)
                sorts[node] = inverted
            elif pname == 'limit':
                paging = int(pval)
            elif pname == 'page':
                page = int(pval)
            elif pname == 'raw':
                raw = self._bool(pval)
        query = OpenImmoQuery(1038007)  # Testing
        immobilie = query.immobilie
        immobilie = query.query(immobilie, filters)
        immobilie = query.sort(immobilie, sorts)
        pages = query.page(immobilie, paging)
        result = '<?xml version="1.0" ?>'
        result += self._dtd() if not raw else ''
        result += self._style() if not raw else ''
        result += '<immolist>'
        if page is None:
            c = 0
            for p in pages:
                result += self._print_page(p, c, len(pages))
                c += 1
        else:
            result += self._print_page(pages[page], page, len(pages))
        result += '</immolist>'
        return result

    def _bool(self, s):
        """Converts a string to a booelan value"""
        return s.strip().upper() == 'TRUE'

    def _print_page(self, page, num, pages):
        """Prints a page"""
        result = ('<page ' + 'number="' + str(num)
                  + '" pages="' + str(pages) + '">')
        for re in page:
            result += self._print_realestate(re)
        result += '</page>'
        return result

    def _print_realestate(self, re):
        """Prints a real estate"""
        return str(re).replace('<?xml version="1.0" ?>', '')

    def _style(self):
        """Sets the stylesheet"""
        return ('<?xml-stylesheet type="text/css" '
                'href="http://css.homeinfo.de/test.css" ?>')

    def _dtd(self):
        """Returns the document type definition"""
        return ''   # '<!DOCTYPE openimmo SYSTEM "openimmo_127.xsd">'
