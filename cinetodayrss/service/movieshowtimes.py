"""
Implementation of the movieshowtimes endpoint
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from email.utils import formatdate
from threading import Timer
from typing import Any, Dict, List, Set

import gql
import pytz
from gql.client import Client
from gql.transport.aiohttp import AIOHTTPTransport

from cinetodayrss.settings import settings

_cache = {}
CACHE_CLEAR_INTERVAL_S = 24 * 60 * 60
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


def _to_rss(movies: List[Movie], feed_url: str) -> str:
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")
    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    channel_title = ET.SubElement(channel, "title")
    channel_title.text = "Films dans vos cinémas aujourd'hui"
    channel_link = ET.SubElement(channel, "link")
    channel_link.text = "https://www.allocine.fr/"
    description = ET.SubElement(channel, "description")
    today_date_str = date.today().isoformat()
    description.text = f"Films dans vos cinémas aujourd'hui {today_date_str}"
    for movie in movies:
        item = ET.SubElement(channel, "item")
        item_title = ET.SubElement(item, "title")
        item_title.text = movie.title
        item_link = ET.SubElement(item, "link")
        item_link.text = movie.url
        item_guid = ET.SubElement(item, "guid")
        item_guid.text = movie.url
        item_pub_date = ET.SubElement(item, "pubDate")
        item_pub_date.text = _get_date(movie.id)
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


async def get_movies_rss(theater_ids: List[Movie], feed_url: str) -> str:
    """
    Get the rss feed for the movies
    """
    movies: Set[Movie] = set()
    for theater_id in theater_ids:
        movies_for_theater = await _get_movies_for_theater(theater_id=theater_id)
        movies.update(movies_for_theater)

    sorted_movies = sorted(movies, key=lambda movie: movie.title)

    rss = _to_rss(sorted_movies, feed_url=feed_url)
    return rss


def _get_date(movie_id: int) -> str:
    movie_date = _cache.get(movie_id)
    if not movie_date:
        movie_date = datetime.now(tz=pytz.UTC)
        _cache[movie_id] = movie_date
    return formatdate(movie_date.timestamp())


def _purge_cache():
    date_limit = datetime.now(tz=pytz.UTC) - timedelta(days=90)
    old_movie_ids = [
        movie_id for (movie_id, date) in _cache.items() if date < date_limit
    ]
    for old_movie_id in old_movie_ids:
        _cache.pop(old_movie_id, None)


def schedule_purge_cache():
    """
    Periodically delete old movies from the cache
    """
    _purge_cache()
    timer = Timer(CACHE_CLEAR_INTERVAL_S, schedule_purge_cache)
    timer.daemon = True
    timer.start()
