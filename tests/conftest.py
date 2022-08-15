"""
Test fixtures
"""
from typing import Dict, Any, List

import pytest

from cinetodayrss.service.movieshowtimes import Movie


@pytest.fixture(name="graphql_response_factory")
def fixture_graphql_response_factory():
    """
    :return: a factory to create a graphql response from a list of movies
    """

    def _make_graphql_response(movies: List[Movie]) -> Dict[str, Any]:
        edges = [_make_movie(movie) for movie in movies]
        return {"movieShowtimeList": {"edges": edges}}

    def _make_movie(movie: Movie) -> Dict[str, Any]:
        return {
            "node": {
                "movie": {
                    "title": movie.title,
                    "internalId": int(movie.id),
                }
            }
        }

    return _make_graphql_response
