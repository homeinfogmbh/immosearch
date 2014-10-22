"""
WSGI-environ interpreter
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'

__all__ = ['WSGIEnvInterpreter']

from .filter import OpenImmoFilter

class WSGIEnvInterpreter():
    """
    Class that interprets and translates WSGI 
    environment variables into a filter query
    """
    __PATH_SEP = '/'
    __REQ_SEP = '?'
    __PARAM_SEP = '&'
    __ASS_SEP = '='
    __LIST_SEP = ','
    __ATTR_SEP = '%'
    
    @property
    def PATH_SEP(self):
        """
        Returns the path separator
        """
        return self.__PATH_SEP
    
    @property
    def REQ_SEP(self):
        """
        Returns the request separator
        """
        return self.__REQ_SEP
    
    @property
    def PARAM_SEP(self):
        """
        Returns the parameter (= argument) separator
        """
        return self.__PARAM_SEP
    
    @property
    def ASS_SEP(self):
        """
        Returns the assignment separator
        """
        return self.__ASS_SEP

    @property
    def LIST_SEP(self):
        """
        Returns the list separator
        """
        return self.__LIST_SEP

    @property
    def ATTR_SEP(self):
        """
        Returns the attribute separator
        """
        return self.__ATTR_SEP
    
    def parse(self, query_string):
        """Parses a URI for query commands"""
        params = query_string.split(self.PARAM_SEP)
        filters = {}
        sorts = {}
        paging = None
        page = None
        raw = False
        for p in params:
            param_path = p.split(self.ASS_SEP)
            pname = param_path[0]
            pval = param_path[1]
            if pname == 'filter':
                node, values_, inverted_ = pval.split(self.ATTR_SEP)
                values = values_.split(self.LIST_SEP)
                inverted = self._bool(inverted_)
                filters[node] = (values, inverted)
            elif pname == 'sort':
                node, inverted_ = pval.split(self.ATTR_SEP)
                inverted = self._bool(inverted_)
                sorts[node] = inverted
            elif pname == 'limit':
                paging = int(pval)
            elif pname == 'page':
                page = int(pval)
            elif raw == 'raw':
                raw = self._bool(pval)
        oif = OpenImmoFilter(1038007)
        immobilie = oif.immobilie
        immobilie = oif.filter(immobilie, filters)
        immobilie = oif.sort(immobilie, sorts)
        pages = oif.page(immobilie, paging)
        result = '<?xml version="1.0" ?>'
        result += self._dtd()
        result += self._style()
        result += '<immolist>'
        if page != None:
            result += self._print_page(pages[page], page, len(pages))
        else:
            c = 0
            for p in pages:
                result += self._print_page(p, c, len(pages))
                c += 1
        result += '</immolist>'
        return result
    
    def _bool(self, s):
        """Converts a string to a booelan value"""
        return s.strip().upper() == 'TRUE'
    
    def _print_page(self, page, num, pages):
        """Prints a page"""
        result = '<page ' + 'number="' + str(num) + '" pages="' + str(pages) + '">'
        for re in page:
            result += self._print_realestate(re)
        result += '</page>'
        return result
    
    def _print_realestate(self, re):
        """Prints a real estate"""
        return str(re).replace('<?xml version="1.0" ?>', '')
    
    def _style(self):
        """Sets the stylesheet"""
        return '<?xml-stylesheet type="text/css" href="http://css.homeinfo.de/test.css" ?>'
    
    def _dtd(self):
        """Returns the document type definition"""
        return ''#'<!DOCTYPE openimmo SYSTEM "openimmo_127.xsd">'