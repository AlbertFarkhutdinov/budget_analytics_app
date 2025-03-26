from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    s3_endpoint_url: str = ''
    s3_bucket: str = ''
    s3_access_key_id: str = ''
    s3_secret_access_key: str = ''

    model_config = SettingsConfigDict(
        env_file='src/backend/reports_app/.env',
        env_file_encoding='utf-8',
    )
