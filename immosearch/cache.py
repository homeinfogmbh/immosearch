"""Real estate data caching"""

from openimmodb import Immobilie
from datetime import datetime, timedelta

__all__ = ['CacheManager']


class CacheManager():
    """Caches real estates"""

    def __init__(self, user, cache, refresh=3600):
        """Sets the user and cache"""
        self.user = user
        self.cache = cache
        self.refresh = refresh

    def __iter__(self):
        """Iterates over the user's real estates"""
        cid = self.user.cid
        now = datetime.now()

        try:
            cached_data = self.cache[cid]
        except KeyError:
            real_estates = [i.to_dom() for i in Immobilie.of(cid)]
            self.cache[cid] = (real_estates, now)

            yield from real_estates
        else:
            real_estates, cache_time = cached_data

            if now - cache_time >= timedelta(seconds=self.refresh):
                real_estates = [i.to_dom() for i in Immobilie.of(cid)]
                self.cache[cid] = (real_estates, now)

            yield from real_estates
