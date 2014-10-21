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
        for p in params:
            param_path = p.split(self.ASS_SEP)
            pname = param_path[0]
            pval = param_path[1]
            if pname == 'filter':
                node, values_, inverted_ = pval.split(self.ATTR_SEP)
                values = values_.split(self.LIST_SEP)
                inverted = True if inverted_.upper() == 'TRUE' else False
                filters[node] = (values, inverted)
            elif pname == 'sort':
                node, inverted_ = pval.split(self.ATTR_SEP)
                inverted = True if inverted_.upper() == 'TRUE' else False
                sorts[node] = inverted
            elif pname == 'page':
                paging = int(pval)
        oif = OpenImmoFilter(1038007)
        immobilie = oif.immobilie
        immobilie = oif.filter(immobilie, filters)
        immobilie = oif.sort(immobilie, sorts)
        pages = oif.page(immobilie, paging)
        result = ""
        for page in pages:
            result += "Page:<br/>"
            for re in page:
                result += str(re)
            result += "<br/><br/>"
        return result