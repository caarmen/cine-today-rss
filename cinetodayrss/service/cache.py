"""
Cache of movie data
"""

import datetime as dt
from diskcache import Cache


_CACHE_TIMEOUT_S = 90 * 24 * 60 * 60  # 90 days in seconds


class MovieCache:
    """
    Cache of movie data
    """

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    def get_date(
        self,
        movie_id: int,
    ) -> dt.datetime:
        """
        Get the date this movie was last recorded.
        """
        with Cache(
            directory=self._cache_dir,
        ) as cache:
            movie_date: dt.datetime | None = cache.get(str(movie_id))
            if not movie_date:
                movie_date = dt.datetime.now(tz=dt.timezone.utc)
                cache.set(
                    key=str(movie_id),
                    value=movie_date,
                    expire=_CACHE_TIMEOUT_S,
                )

        return movie_date

    def clear(self):
        """
        Remove all movies from the cache.
        """
        with Cache(
            directory=self._cache_dir,
        ) as cache:
            cache.clear()
