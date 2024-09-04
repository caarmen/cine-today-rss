"""
Implementation of the movieshowtimes endpoint
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, date
from email.utils import formatdate
from typing import Any, Dict, List, Set

import gql
from gql.client import Client
from gql.transport.aiohttp import AIOHTTPTransport

from cinetodayrss.service.cache import MovieCache
from cinetodayrss.settings import settings

_cache = MovieCache(settings.cache_dir)
ALLOCINE_GRAPHQL_URL = "https://graph.allocine.fr/v1/public"
ALLOCINE_FILM_URL_TEMPLATE = "https://www.allocine.fr/film/fichefilm_gen_cfilm={}.html"


@dataclass(eq=True, frozen=True)
class Movie:
    """
    Details about a movie
    """

    # pylint: disable=invalid-name
    id: str
    title: str

    @property
    def url(self) -> str:
        """
        The url of the movie
        """
        return ALLOCINE_FILM_URL_TEMPLATE.format(self.id)


_query = gql.gql(
    """
query MovieWithShowtimesList($theaterId: String!, $from: DateTime!, $to: DateTime!) {
    movieShowtimeList(
        theater: $theaterId
        from: $from
        to: $to
        first: 50
        order: [REVERSE_RELEASE_DATE, WEEKLY_POPULARITY]
    )  {
        edges  {
            node {
                movie {
                    title
                    internalId
                }
            }
        }
    }
}
"""
)


def _to_rss(
    movies: List[Movie],
    feed_url: str,
) -> str:
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")
    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    ET.SubElement(channel, "title").text = "Films dans vos cinémas aujourd'hui"
    ET.SubElement(channel, "link").text = "https://www.allocine.fr/"
    today_date_str = date.today().isoformat()
    ET.SubElement(channel, "description").text = (
        f"Films dans vos cinémas aujourd'hui {today_date_str}"
    )
    for movie in movies:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = movie.title
        ET.SubElement(item, "link").text = movie.url
        ET.SubElement(item, "guid").text = movie.url
        ET.SubElement(item, "pubDate").text = _get_date(
            movie.id,
        )
    ET.indent(rss, space="    ")
    return ET.tostring(rss, xml_declaration=True, encoding="utf-8")


def _edge_to_movie(edge: Dict[str, Any]) -> Movie:
    movie = edge["node"]["movie"]
    return Movie(id=movie["internalId"], title=movie["title"])


def _response_to_movies(response: Dict[str, Any]) -> List[Movie]:
    edges = response["movieShowtimeList"]["edges"]
    return [_edge_to_movie(edge) for edge in edges]


async def _get_movies_for_theater(theater_id: str) -> List[Movie]:
    datetime_from = (
        datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    )
    datetime_to = datetime.now().replace(hour=23, minute=59, second=59).isoformat()
    params = {
        "theaterId": theater_id,
        "from": datetime_from,
        "to": datetime_to,
    }
    async with Client(
        transport=AIOHTTPTransport(
            url=ALLOCINE_GRAPHQL_URL,
            headers={
                "Authorization": f"Bearer {settings.authorization}",
            },
        ),
        fetch_schema_from_transport=True,
        serialize_variables=True,
        parse_results=True,
    ) as client:
        response = await client.execute(_query, variable_values=params)
        return _response_to_movies(response)


async def get_movies_rss(
    theater_ids: List[Movie],
    feed_url: str,
) -> str:
    """
    Get the rss feed for the movies
    """
    movies: Set[Movie] = set()
    for theater_id in theater_ids:
        movies_for_theater = await _get_movies_for_theater(theater_id=theater_id)
        movies.update(movies_for_theater)

    sorted_movies = sorted(movies, key=lambda movie: movie.title)

    rss = _to_rss(
        sorted_movies,
        feed_url=feed_url,
    )
    return rss


def _get_date(
    movie_id: int,
) -> str:
    movie_date = _cache.get_date(movie_id)
    return formatdate(movie_date.timestamp())
