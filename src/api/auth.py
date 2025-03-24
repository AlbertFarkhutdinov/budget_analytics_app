import logging

from fastapi import APIRouter
from pydantic import BaseModel

from auth_app.auth import AuthSettings, CognitoClient
from custom_logging import config_logging

logger = logging.getLogger(__name__)


class UserLogin(BaseModel):
    username: str
    password: str


class UserConfirm(BaseModel):
    username: str
    confirmation_code: str = ''


config_logging()
settings = AuthSettings()
cognito_client = CognitoClient(settings)
auth_router = APIRouter()


@auth_router.post('/register')
def register(user: UserLogin) -> dict[str, str]:
    logger.info('Received register request.')
    return cognito_client.register_user(user.username, user.password)


@auth_router.post('/confirm')
def confirm(user: UserConfirm) -> dict[str, str]:
    logger.info('Received confirm request.')
    return cognito_client.confirm_user(user.username, user.confirmation_code)


@auth_router.post('/login')
def login(user: UserLogin) -> dict[str, str]:
    logger.info('Received login request.')
    return cognito_client.login_user(user.username, user.password)
