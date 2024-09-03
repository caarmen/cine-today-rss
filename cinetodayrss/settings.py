"""
Settings module
"""

from pydantic_settings import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """
    Settings for the app
    """

    authorization: str = ""


settings = Settings(_env_file="prod.env")
