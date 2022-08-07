"""
Implementation of the movieshowtimes endpoint
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Dict, List
import xml.etree.ElementTree as ET

from gql.client import Client
from gql.transport.aiohttp import AIOHTTPTransport
import gql

from cinetodayrss.settings import settings


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
        return f"https://www.allocine.fr/film/fichefilm_gen_cfilm={self.id}.html"


ALLOCINE_URL = "https://graph.allocine.fr/v1/mobile"
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


def _to_rss(movies: List[Movie]) -> str:
    rss = ET.Element("rss")
    channel = ET.SubElement(rss, "channel")
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
    ET.indent(rss, space="    ")
    return ET.tostring(rss, xml_declaration=True, encoding="utf-8")


def _edge_to_movie(edge: Dict[str, Any]) -> Movie:
    movie = edge["node"]["movie"]
    return Movie(id=movie["internalId"], title=movie["title"])


def _response_to_movies(response: str) -> List[Movie]:
    edges = response["movieShowtimeList"]["edges"]
    all_movies = [_edge_to_movie(edge) for edge in edges]
    unique_movies = list(set(all_movies))
    return unique_movies


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
            url=ALLOCINE_URL,
            headers={
                "Authorization": f"Bearer {settings.authorization}",
                "AC-Auth-Token": settings.ac_auth_token,
            },
        ),
        fetch_schema_from_transport=True,
        serialize_variables=True,
        parse_results=True,
    ) as client:
        response = await client.execute(_query, variable_values=params)
        return _response_to_movies(response)


async def get_movies_rss(theater_ids: List[Movie]) -> str:
    """
    Get the rss feed for the movies
    """
    movies: List[Movie] = []
    for theater_id in theater_ids:
        movies_for_theater = await _get_movies_for_theater(theater_id=theater_id)
        movies.extend(movies_for_theater)

    sorted_movies = sorted(movies, key=lambda movie: movie.title)

    rss = _to_rss(sorted_movies)
    return rss
