"""
Provides dependencies for FastAPI dependency injection
"""

from typing import Annotated

from fastapi import Depends
from cinetodayrss.service.cache import MovieCache
from cinetodayrss.settings import settings


def get_cache_dir() -> str:
    """
    :return: the location of the folder containing the movie cache.
    """

    return settings.cache_dir


def get_movie_cache(cache_dir2: Annotated[str, Depends(get_cache_dir)]) -> MovieCache:
    """
    :return: the MovieCache.
    """
    return MovieCache(cache_dir=cache_dir2)
