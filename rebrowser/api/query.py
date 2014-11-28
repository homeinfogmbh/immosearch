"""
OpenImmo data querying
"""
import openimmo

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'
__all__ = ['OpenImmoQuery']


class SortableRealEstate():
    """
    An OpenImmo™ immobilie wrapper, that can be sorted
    """
    keys = []
    __immobilie = None
    
    def __init__(self, immobilie, keys=[]):
        """Creates a new instance"""
        self.__immobilie = immobilie
        self.keys = keys
        
    @property
    def immobilie(self):
        """Returns the OpenImmo™ immobilie"""
        return self.__immobilie
        
    def __eq__(self, other):
        """Equality comparison"""
        return self.keys == other.keys
    
    def __gt__(self, other):
        """Greater-than comparison"""
        return self.keys > other.keys
    
    def __lt__(self, other):
        """Less-than comparison"""
        return self.keys < other.keys
    
    def __ge__(self, other):
        """Greater-than or equal comparison"""
        return self.__eq__(other) or self.__gt__(other)
    
    def __le__(self, other):
        """Less-than or equal comparison"""
        return self.__eq__(other) or self.__lt__(other)
    

class OpenImmoQuery():
    """
    A class that filters OpenImmo™-formatted real estate data
    """
    def __init__(self, cid):
        """Creates a new filter instance"""
        self.__cid = cid
        
    @property
    def cid(self):
        """Returns the customer identifier"""
        return self.__cid
        
    @property
    def _xmlfile(self):
        """Returns the customer's XML file"""
        return '/home/ftpuser/expose-tv/<cid>/<cid>/liste.xml'\
            .replace('<cid>', str(self.cid)) 
    
    @property
    def _openimmo(self):
        """Returns the customer's OpenImmo™ data"""
        with open(self._xmlfile, 'rb') as f:
            return openimmo.CreateFromDocument(f.read())
        
    @property
    def immobilie(self):
        """Returns a list of OpenImmo™-style immobilie"""
        result = []
        for anbieter in self._openimmo.anbieter:
            for immobilie in anbieter.immobilie:
                result.append(immobilie)
        return result
    
    def _filter(self, immobilie, node, values, inverted=False):
        """Filter a list of  OpenImmo™-style <immobilie> where <node> 
        is in <values> or their complement iff <inverted>"""
        node_path = node.split('.')
        positive_match = []
        negative_match = []
        upper_values = [v.upper() for v in values]
        for i in immobilie:
            n = i
            for e in node_path:
                n = getattr(n, e)
            if str(n).upper() in upper_values:
                positive_match.append(i)
            else:
                negative_match.append(i)
        return negative_match if inverted else positive_match

    def filter(self, immobilie, nodes):
        """Filter a list of OpenImmo™-style <immobilie> by a rules list like:
        {<node>: ([<value>, ..], <inverted>)}"""
        for node in nodes:
            values, inverted = nodes[node]
            immobilie = self._filter(immobilie, node, values, inverted)
        return immobilie
    
    def _index(self, sres, node, inverted):
        """Indexes a list of SortableRealEstates <sres> 
        for <node> either <inverted> or not.
        Returns an indexed list of immobilie, like:
        [((<k1>, <k2>, ..), <immobilie>), ..]"""
        node_path = node.split('.')
        values = []     # The actual real estates
        # Sets the new keys
        for re in sres:
                k = re.immobilie
                for e in node_path:
                    k = getattr(k, e)
                values.append(SortableRealEstate(re.immobilie, [k]))
        sorted_values = sorted(values)
        # Inverts keys if desired
        if inverted:
            c = 1
            l = len(sorted_values)
            inv = []
            for s in sorted_values:
                inv.append(SortableRealEstate(s.immobilie, 
                                              sorted_values[l-c].keys))
            sorted_values = sorted(inv)
            c += 1
        # Appends new keys to sorted real estates
        result = []
        for s in sorted_values:
            for r in sres:
                if s.immobilie == r.immobilie:
                    result.append(SortableRealEstate(s.immobilie, 
                                                     r.keys + s.keys))
        return result
    
    def sort(self, immobilie, nodes):
        """Sorts a list of OpenImmo™-style <immobilie> by a dictionary like: 
        {<node>: <inverted>, ..}"""
        if nodes:
            sres = [SortableRealEstate(i) for i in immobilie]
            for node in nodes:
                inverted = nodes[node]
                sres = self._index(sres, node, inverted)
            # Sort an remove indexes
            return [s.immobilie for s in sorted(sres)] 
        else:
            return immobilie
    
    def page(self, immobilie, limit=None):
        """Splits a list of OpenImmo™-style <immobilie> into a list of lists, 
        each list not longer than the provided limit"""
        pages = []
        if not limit:
            return [immobilie]
        else:
            page = []
            for i in immobilie:
                if len(page) < limit:
                    page.append(i)
                else:
                    pages.append(page)
                    page = []
            if page:
                pages.append(page)
            return pages