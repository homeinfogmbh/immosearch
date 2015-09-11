"""Real estate data caching"""
from openimmodb3.db import Immobilie
from datetime import datetime, timedelta

__all__ = ['CacheManager']


class CacheManager():
    """Caches real estates"""

    def __init__(self, user, cache, refresh=3600):
        """Sets the user and cache"""
        self._user = user
        self._cache = cache
        self._refresh = refresh

    def __iter__(self):
        """Iterates over the user's real estates"""
        cid = self._user.cid
        if self._cache is None:
            for i in Immobilie.by_cid(cid):
                yield i.immobilie
        else:
            now = datetime.now()
            try:
                cached_data = self._cache[cid]
            except KeyError:
                real_estates = [i.immobilie for i in Immobilie.by_cid(cid)]
                self._cache[cid] = (real_estates, now)
                yield from real_estates
            else:
                real_estates, cache_time = cached_data
                if now - cache_time >= timedelta(seconds=self._refresh):
                    real_estates = [i.immobilie for i in Immobilie.by_cid(cid)]
                    self._cache[cid] = (real_estates, now)
                yield from real_estates
