"""
Settings module
"""

from pathlib import Path
from pydantic_settings import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """
    Settings for the app
    """

    cache_dir: Path = Path("/tmp/cine-today-rss-cache/")


settings = Settings(_env_file="prod.env")
