"""Element paging"""

from typing import Any, Iterable, Optional


__all__ = ['Pager']


class Pager:    # pylint: disable=R0903
    """Browses through pages"""

    def __init__(self, items: Iterable[Any], limit: Optional[int] = None,
                 page: Optional[int] = None):
        """Sets the respective items and the page size limit"""
        self.items = items
        self.limit = limit
        self.page = page or 0

    def __iter__(self) -> Any:
        """Yields items of nth page"""
        if self.limit is None:
            yield from self.items
            return

        start = self.page * self.limit
        end = (self.page + 1) * self.limit - 1

        for i, item in enumerate(self.items):
            if start <= i <= end:
                yield item
