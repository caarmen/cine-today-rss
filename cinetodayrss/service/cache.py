"""
Cache of movie data
"""

import datetime as dt
from threading import Timer

_CACHE_CLEAR_INTERVAL_S = 24 * 60 * 60


class MovieCache:
    """
    Cache of movie data
    """

    def __init__(self):
        self._cache: dict[int, dt.datetime] = {}

    def get_date(
        self,
        movie_id: int,
    ) -> dt.datetime:
        """
        Get the date this movie was last recorded.
        """
        movie_date: dt.datetime | None = self._cache.get(movie_id)
        if not movie_date:
            movie_date = dt.datetime.now(tz=dt.timezone.utc)
            self._cache[movie_id] = movie_date

        return movie_date

    def purge_old_movies(self):
        """
        Remove movies from the cache which were recorded "a long time ago".
        """
        date_limit = dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=90)
        old_movie_ids = [
            movie_id for (movie_id, date) in self._cache.items() if date < date_limit
        ]
        for old_movie_id in old_movie_ids:
            self._cache.pop(old_movie_id, None)

    def schedule_purge_cache(self):
        """
        Periodically delete old movies from the cache
        """
        self.purge_old_movies()
        timer = Timer(_CACHE_CLEAR_INTERVAL_S, self.schedule_purge_cache, self)
        timer.daemon = True
        timer.start()

    def clear(self):
        """
        Remove all movies from the cache.
        """
        self._cache.clear()
