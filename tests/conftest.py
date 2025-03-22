"""
Test fixtures
"""

from pathlib import Path
from typing import Dict, Any, List

import pytest

from cinetodayrss.dependencies import get_cache_dir
from cinetodayrss.main import app
from cinetodayrss.service.movieshowtimes import Movie


@pytest.fixture(autouse=True)
def override_cache_dir(tmp_path: Path):
    """
    Override the cache location for tests.
    """
    app.dependency_overrides[get_cache_dir] = lambda: str(tmp_path)


@pytest.fixture(name="cinetoday_response_factory")
def fixture_cinetoday_response_factory():
    """
    :return: a factory to create a cinetoday response from a list of movies
    """

    def _make_response(movies: List[Movie]) -> Dict[str, Any]:
        return {
            "results": [
                {
                    "movie": {
                        "title": movie.title,
                        "internalId": int(movie.id),
                    }
                }
                for movie in movies
            ],
        }

    return _make_response
