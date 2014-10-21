"""
Session management
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '10.10.2014'

__all__ = ['OpenImmoFilter']

import openimmo

class OpenImmoFilter():
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
        node_path = inverted(node.split('.'))
        positive_match = []
        negative_match = []
        for i in immobilie:
            n = i
            while node_path:
                n = getattr(n, node_path.pop())
            if n in values:
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
    
    def _index(self, immobilie, node, inverted):
        """Indexes a list of OpenImmo™-style <immobilie> 
        for <node> either <inverted> or not.
        Returns an indexed list of immobilie, like:
        [((<k1>, <k2>, ..), <immobilie>), ..]"""
        node_path = node.split('.')
        old_keys = []   # Already existing keys
        new_keys = []   # New keys
        values = []     # The actual real estates
        result = []     # The result
        for i in immobilie:
            try:
                o, v = i    # Splits <immobilie> into old key and value pair ...
            except:
                o = ()      # ... or initializes empty old key tuple ...
                v = i       # ... and starts with real estate directly
            finally:
                old_keys.append(o)  # Stores old key
                k = v               # Starts at real estate
                for e in node_path: # Gets the new key
                    k = getattr(k, e)
                new_keys.append(k)  # Stores new keys
                values.append((k, v))    # Stores new key, value pairs
        values = [v for _, v in sorted(values)] # Sorts new key / value pairs
        new_keys = sorted(new_keys) # Sorts new keys accordingly
        new_keys = reversed(new_keys) if inverted else new_keys
        c = 0
        for n in new_keys:
            k = old_keys[c] + (n,)
            result.append((k, values[c]))
            c += 1
        return result
    
    def sort(self, immobilie, nodes):
        """Sorts a list of OpenImmo™-style <immobilie> by a dictionary like: 
        {<node>: <inverted>, ..}"""
        for node in nodes:
            inverted = nodes[node]
            immobilie = self._index(immobilie, node, inverted)
        # Sort an remove indexes
        return [i for _, i in sorted(immobilie)] if nodes else immobilie
    
    def page(self, immobilie, limit=None):
        """Splits a list of OpenImmo™-style <immobilie> into a list of lists, 
        each list not longer than the provided limit"""
        pages = []
        if not limit:
            return [immobilie]
        else:
            page = []
            while immobilie:
                if len(page) < limit:
                    page.append(immobilie.pop())
                else:
                    pages.append(page)
                    page = []
            if page:
                pages.append(page)
            return pages