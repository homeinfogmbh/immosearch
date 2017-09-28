"""Real estate data caching."""

from datetime import datetime, timedelta

from openimmodb import Immobilie

__all__ = ['RealEstateCache']


class RealEstateCache:
    """Caches real estates."""

    def __init__(self, customer, interval=3600):
        """Sets the user and cache."""
        self.customer = customer
        self.timestamp = None
        self.real_estates = None
        self._interval = interval

    def __hash__(self):
        """Returns a unique hash."""
        return hash((self.__class__, self.customer))

    @property
    def interval(self):
        """Returns the refresh interval."""
        return timedelta(seconds=self._interval)

    @interval.setter
    def interval(self, interval):
        """Sets the refresh interval inseconds."""
        self._interval = interval

    @property
    def real_estates(self):
        """Yields real estates for the respective customer."""
        for real_estate in Immobilie.by_customer(self.customer.id):
            yield real_estate.to_dom()

    def _update(self):
        """Updates the cache for the respective customer."""
        self.timestamp = datetime.now()
        self.real_estates = tuple(self.real_estates)

    def update(self):
        """Conditionally updates the cache for the respective
        customer iff it is out of date or uninitialized.
        """
        if self.timestamp is None or self.real_estates is None:
            self.update()
        elif datetime.now() - self.timestamp >= self.interval:
            self.update()

    def __iter__(self):
        """Iterates over the user's real estates."""
        self.update()

        for real_estate in self.real_estates:
            yield real_estate
