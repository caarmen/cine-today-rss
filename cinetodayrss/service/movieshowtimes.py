"""
Implementation of the movieshowtimes endpoint
"""

import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from datetime import date
from email.utils import formatdate
from typing import Any, Dict, List, Set

import httpx

from cinetodayrss.service.cache import MovieCache

logger = logging.getLogger(__name__)

ALLOCINE_API_URL = "https://www.allocine.fr/_/showtimes"
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


def _to_rss(
    movies: List[Movie],
    feed_url: str,
    movie_cache: MovieCache,
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
            movie_cache,
        )
    ET.indent(rss, space="    ")
    return ET.tostring(rss, xml_declaration=True, encoding="utf-8")


def _response_to_movies(response: Dict[str, Any]) -> List[Movie]:
    results = response["results"]
    return [
        Movie(id=item["movie"]["internalId"], title=item["movie"]["title"])
        for item in results
    ]


async def _get_movies_for_theater(theater_id: str) -> List[Movie]:
    date_now = date.today()
    date_now_fmt = date.strftime(date_now, "%Y-%m-%d")
    url = f"{ALLOCINE_API_URL}/theater-{theater_id}/d-{date_now_fmt}/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url)
    if not response.is_success:
        logger.error(f"Error fetching {url}: response text {response.text}")
        return []
    return _response_to_movies(response.json())


async def get_movies_rss(
    theater_ids: List[Movie],
    feed_url: str,
    movie_cache: MovieCache,
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
        movie_cache=movie_cache,
    )
    return rss


def _get_date(
    movie_id: int,
    movie_cache: MovieCache,
) -> str:
    movie_date = movie_cache.get_date(movie_id)
    return formatdate(movie_date.timestamp())
