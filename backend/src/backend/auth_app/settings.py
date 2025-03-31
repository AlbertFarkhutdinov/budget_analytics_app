"""The module providing Pydantic settings for authentication configuration."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """
    Pydantic settings model for authentication configuration.

    This class is used to load and validate authentication-related settings
    from environment variables or a configuration file.

    Attributes
    ----------
    cognito_user_pool_id : str
        The Cognito user pool ID.
    cognito_client_id : str
        The Cognito client ID.
    cognito_region : str
        The AWS region where the Cognito pool is located.
    cognito_client_secret : str
        The secret associated with the Cognito client.
    model_config : SettingsConfigDict
        Configuration for loading settings from an environment file.
        The file is expected to be located at 'src/backend/auth_app/.env'.

    """

    cognito_user_pool_id: str = ''
    cognito_client_id: str = ''
    cognito_region: str = ''
    cognito_client_secret: str = ''

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.joinpath('.env'),
        env_file_encoding='utf-8',
    )
