from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    cognito_user_pool_id: str = ''
    cognito_client_id: str = ''
    cognito_region: str = ''
    cognito_client_secret: str = ''

    model_config = SettingsConfigDict(
        env_file='src/backend/auth_app/.env',
        env_file_encoding='utf-8',
    )
