"""The module that provides Pydantic settings for the S3 storage."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    """
    Configuration settings for S3 storage.

    Attributes
    ----------
    s3_endpoint_url : str
        The URL of the S3-compatible storage endpoint.
    s3_bucket : str
        The name of the S3 bucket.
    s3_access_key_id : str
        The access key ID for S3 authentication.
    s3_secret_access_key : str
        The secret access key for S3 authentication.
    model_config : SettingsConfigDict
        Configuration for loading settings from an environment file.
        The file is expected to be located at 'src/backend/reports_app/.env'.

    """

    s3_endpoint_url: str = ''
    s3_bucket: str = ''
    s3_access_key_id: str = ''
    s3_secret_access_key: str = ''

    model_config = SettingsConfigDict(
        env_file='src/backend/reports_app/.env',
        env_file_encoding='utf-8',
    )
