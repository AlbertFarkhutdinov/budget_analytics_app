from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: int = 5432
    db_name: str = ''

    model_config = SettingsConfigDict(
        env_file='src/backend/entries_app/.env',
        env_file_encoding='utf-8',
    )
