"""Element paging"""

__all__ = ['Pager']


class Pager():
    """Browses through pages"""

    def __init__(self, items, limit=None, page=None):
        """Sets the respective items and the page size limit"""
        self._items = items
        self._limit = limit
        self._page = page

    @property
    def items(self):
        """Returns the items to be paged"""
        return self._items

    @property
    def limit(self):
        """Returns page size limit"""
        return self._limit

    @property
    def page(self):
        """Returns the index of the page to be displayed"""
        return self._page or 0

    def __iter__(self):
        """Yields items of nth page"""
        if self.limit is None:
            yield from self.items
        else:
            i0 = self.page * self.limit
            i1 = (self.page + 1) * self.limit - 1
            for i, item in enumerate(self.items):
                if i0 <= i <= i1:
                    yield item
