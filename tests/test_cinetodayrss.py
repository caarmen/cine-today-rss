"""
Unit tests for cine today rss
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from fastapi.testclient import TestClient
from freezegun import freeze_time
import httpx

from cinetodayrss.main import app
from cinetodayrss.service import movieshowtimes
from cinetodayrss.service.movieshowtimes import ALLOCINE_API_URL, Movie

client = TestClient(app)


def test_rss_feed(respx_mock, cinetoday_response_factory):
    """
    Verify the rss feed has the expected data
    """
    route = respx_mock.get(url__regex=rf"{ALLOCINE_API_URL}/theater.*")
    route.side_effect = [
        httpx.Response(
            200,
            json=cinetoday_response_factory([Movie(id="123", title="Un film drole")]),
        ),
        httpx.Response(
            200,
            json=cinetoday_response_factory(
                [Movie(id="456", title="Un film de drame")]
            ),
        ),
    ]
    response = client.get(
        "/moviesrss?theater_ids=VGhlYXRlcjpDMDE1OQ==&theater_ids=VGhlYXRlcjpQNTc1Ng=="
    )
    assert response.status_code == 200
    rss_doc_root = ET.fromstring(response.content)
    assert rss_doc_root.tag == "rss"
    items = rss_doc_root.find("channel").findall("item")
    assert len(items) == 2
    item = items.pop(0)
    assert item.find("title").text == "Un film de drame"
    assert item.find("link").text == movieshowtimes.ALLOCINE_FILM_URL_TEMPLATE.format(
        456
    )
    assert item.find("guid").text == movieshowtimes.ALLOCINE_FILM_URL_TEMPLATE.format(
        456
    )
    pub_date = item.find("pubDate").text
    assert isinstance(parsedate_to_datetime(pub_date), datetime)

    item = items.pop(0)
    assert item.find("title").text == "Un film drole"
    assert item.find("link").text == movieshowtimes.ALLOCINE_FILM_URL_TEMPLATE.format(
        123
    )
    assert item.find("guid").text == movieshowtimes.ALLOCINE_FILM_URL_TEMPLATE.format(
        123
    )
    pub_date = item.find("pubDate").text
    assert isinstance(parsedate_to_datetime(pub_date), datetime)


def test_date_cache(respx_mock, cinetoday_response_factory):
    """
    Verify that we use the dates from the cache
    """
    now = datetime.now(tz=timezone.utc)
    with freeze_time("1995-12-31 22:10:00") as frozen_date:
        respx_mock.get(url__regex=rf"{ALLOCINE_API_URL}/theater.*").mock(
            httpx.Response(
                200,
                json=cinetoday_response_factory([Movie(id="111", title="Une comédie")]),
            ),
        )
        response = client.get("/moviesrss?theater_ids=VGhlYXRlcjpDMDE1OQ==")
        assert response.status_code == 200
        rss_doc_root = ET.fromstring(response.content)
        items = rss_doc_root.find("channel").findall("item")
        assert len(items) == 1
        item = items.pop(0)
        pub_date_text = item.find("pubDate").text
        pub_date = parsedate_to_datetime(pub_date_text)
        assert pub_date.year == 1995
        assert pub_date.month == 12
        assert pub_date.day == 31
        assert pub_date.hour == 22
        assert pub_date.minute == 10
        assert pub_date.second == 0

        frozen_date.move_to(now)

        response = client.get("/moviesrss?theater_ids=VGhlYXRlcjpDMDE1OQ==")
        assert response.status_code == 200
        rss_doc_root = ET.fromstring(response.content)
        items = rss_doc_root.find("channel").findall("item")
        assert len(items) == 1
        item = items.pop(0)
        pub_date_text = item.find("pubDate").text
        pub_date = parsedate_to_datetime(pub_date_text)
        assert pub_date.year != 1995


def test_remove_duplicates(respx_mock, cinetoday_response_factory):
    """
    If a movie is showing in multiple theaters, verify that it appears only once in the rss feed
    """
    route = respx_mock.get(url__regex=rf"{ALLOCINE_API_URL}/theater.*")
    route.side_effect = [
        httpx.Response(
            200,
            json=cinetoday_response_factory(
                [
                    Movie(
                        id="296393", title="Les Vieux fourneaux 2 : bons pour l’asile"
                    ),
                ]
            ),
        ),
        httpx.Response(
            200,
            json=cinetoday_response_factory(
                [
                    Movie(
                        id="296393", title="Les Vieux fourneaux 2 : bons pour l’asile"
                    ),
                ]
            ),
        ),
    ]
    response = client.get(
        "/moviesrss?theater_ids=VGhlYXRlcjpDMDE1OQ==&theater_ids=VGhlYXRlcjpQNTc1Ng=="
    )
    assert response.status_code == 200
    rss_doc_root = ET.fromstring(response.content)
    assert rss_doc_root.tag == "rss"
    items = rss_doc_root.find("channel").findall("item")
    assert len(items) == 1
    item = items.pop()
    title = item.find("title")
    assert title.text == "Les Vieux fourneaux 2 : bons pour l’asile"
