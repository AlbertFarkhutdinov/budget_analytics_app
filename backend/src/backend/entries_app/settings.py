"""The module providing Pydantic settings for the database connection."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """
    Pydantic settings model for the database connection.

    Attributes
    ----------
    db_user : str
        Database username.
    db_password : str
        Database password.
    db_host : str
        Database host address.
    db_port : int
        Database port number (default: 5432).
    db_name : str
        Name of the database.
    model_config : SettingsConfigDict
        Configuration for loading settings from an environment file.
        The file is expected to be located at 'src/backend/entries_app/.env'.

    """

    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: int = 5432
    db_name: str = ''

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.joinpath('.env'),
        env_file_encoding='utf-8',
    )
