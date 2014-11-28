"""
Real estate filter
"""
__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '28.11.2014'
__all__ = ['Filter']


class Filter():
    """
    A real estate filter
    """
    def __init__(self, fdict=None):
        """Initializes with a filter dictionary"""
        self.__fdict = {} if fdict is None else fdict

    @property
    def fdict(self):
        """Returns the filter dictionary"""
        return self.__fdict

    def add_rule(self, node, ):
        pass


class Rule():
    """
    A filter rule
    """
    def __init__(self, node, op, values):
        """Initializes a filter rule"""
        self.__node = node
        self.__op = op
        self.__values = values

    @property
    def node(self):
        """Returns the filtering node"""
        return self.__node

    @property
    def op(self):
        """Returns the desired operation"""
        return self.__op

    @property
    def values(self):
        """Returns the filter values"""
        return self.__values

    def _node_data(self, real_estate):
        """Returns the data of the targeted node"""
        if self.node == 'openimmo_obid':
            return str(real_estate.verwaltung_techn.openimmo_obid)
        elif self.node == 'wohnflaeche':
            # TODO: implement further
            pass

    def apply(self, real_estates):
        """Applies the rule on an iterable real_estates"""
        for real_estate in real_estates:
            if self._filter(real_estate):
                yield real_estate
        node_data = self._node_data()
        # TODO: implement further
