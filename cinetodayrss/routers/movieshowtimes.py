"""
Router to list movies with their showtimes
"""
from typing import List
from fastapi import APIRouter, Query, Response
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
    theater_ids: List[str] = Query(default=[]),
):
    content = await get_movies_rss(theater_ids)
    return Response(
        content=content,
        media_type="application/rss+xml; charset=utf-8",
    )
