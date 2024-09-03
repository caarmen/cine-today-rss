"""
Entry point to the cinetoday rss server
"""

import os
from fastapi import FastAPI
import uvicorn
from cinetodayrss.routers import movieshowtimes

app = FastAPI(
    openapi_url=None,
    redoc_url=None,
    docs_url=None,
)
app.include_router(movieshowtimes.router)


if __name__ == "__main__":
    uvicorn.run(
        "cinetodayrss.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("UVICORN_PORT", "8000")),
    )
