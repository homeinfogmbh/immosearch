"""Element paging"""

__author__ = 'Richard Neumann <r.neumann@homeinfo.de>'
__date__ = '24.02.2015'
__all__ = ['Pager']


class Pager():
    """Browses through pages"""

    def __init__(self, items, limit=None):
        """Sets the respective items and the page size limit"""
        self._items = items
        self._limit = limit

    @property
    def items(self):
        """Returns the items to be paged"""
        return self._items

    @property
    def limit(self):
        """Returns page size limit"""
        return self._limit

    def page(self, n):
        """Yields items of nth page"""
        if self.limit is None:
            yield from self.items
        else:
            i0 = n * self.limit
            i1 = (n + 1) * self.limit - 1
            for i, item in enumerate(self.items):
                if i >= i0 and i <= i1:
                    yield item
