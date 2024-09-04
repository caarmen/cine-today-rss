"""
Router to list movies with their showtimes
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, Request, Response
from cinetodayrss.dependencies import get_movie_cache
from cinetodayrss.service.cache import MovieCache
from cinetodayrss.service.movieshowtimes import get_movies_rss


router = APIRouter()


@router.get(
    "/moviesrss",
    responses={
        200: {},
        422: {
            "description": "The request parameters were understood, but could not be processed",
        },
    },
)
async def movies_rss(
    movie_cache: Annotated[MovieCache, Depends(get_movie_cache)],
    request: Request,
    theater_ids: List[str] = Query(default=[]),
):
    content = await get_movies_rss(
        theater_ids,
        feed_url=str(request.url),
        movie_cache=movie_cache,
    )
    return Response(
        content=content,
        media_type="application/rss+xml; charset=utf-8",
    )
