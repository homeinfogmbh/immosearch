"""
OpenImmo™-<immobilie> rendering
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '22.10.2014'

from os.path import isfile
import openimmo

class HTMLRealEstate():
    """
    A wrapper that renders an OpenImmo™-<immobile>-style real estate data into an HTML template
    """
    __immobilie = None
    __template = None
    __tag_open = None
    __tag_close = None
    
    def __init__(self, immobilie, template, tag_open='<immobilie ', tag_close='/>'):
        """Creates a new instance"""
        if type(immobilie) == str:
            self.__immobilie = openimmo.CreateFromDocument(immobilie)
        else:
            self.__immobilie = immobilie
        if isfile(template):
            with open(template, 'r') as f:
                self.__template = f.read()
        else:
            self.__template = template
        self.__tag_open = tag_open
        self.__tag_close = tag_close
        
    @property
    def _tags(self):
        record = False
        window = ''
        token = self.__tag_open
        tag = ''
        result = []
        for c in self.__template:
            # Records tag content iff in record mode
            if record:
                tag += c
            # Move window
            if len(window) < len(token):
                window += c
            else:
                window = window[1:len(window)] + c
            if window == self.__tag_open:
                record = True
                token = self.__tag_close
                window = ''
            elif window == self.__tag_close:
                record = False
                token = self.__tag_open
                window = ''
                result.append(tag.replace(self.__tag_close, ''))
                tag = ''
        return result
        
    def _getval(self, field):
        """Returns the value of a desired field"""
        subject = self.__immobilie
        for attr in field.split('.'):
            try:
                subject = getattr(subject, attr)
            except:
                subject = 'ERROR'
                break
        return subject
    
    @property
    def _dict(self):
        """Returns the translation dictionary"""
        result = {}
        for k in self._tags:
            v = self._getval(k)
            result[self.__tag_open + k + self.__tag_close] = v
        return result
    
    def render(self):
        """Render the real estate into the HTML template"""
        result = self.__template
        d = self._dict
        for k in d:
            result = result.replace(k, d[k])
        return result