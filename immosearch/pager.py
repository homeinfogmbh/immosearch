"""Element paging"""


__all__ = ['Pager']


class Pager:    # pylint: disable=R0903
    """Browses through pages"""

    def __init__(self, items, limit=None, page=None):
        """Sets the respective items and the page size limit"""
        self.items = items
        self.limit = limit
        self.page = page or 0

    def __iter__(self):
        """Yields items of nth page"""
        if self.limit is None:
            yield from self.items
        else:
            start = self.page * self.limit
            end = (self.page + 1) * self.limit - 1

            for i, item in enumerate(self.items):
                if start <= i <= end:
                    yield item
