"""
Authentication API routes using FastAPI and AWS Cognito.

This module defines authentication-related endpoints for user registration,
confirmation, and login using AWS Cognito.

"""
import logging

from fastapi import APIRouter

from backend.auth_app.cognito_client import CognitoClient
from backend.auth_app.models import UserConfirm, UserLogin
from backend.auth_app.settings import AuthSettings
from custom_logging import config_logging

logger = logging.getLogger(__name__)


config_logging()
settings = AuthSettings()
cognito_client = CognitoClient(settings)
auth_router = APIRouter()


@auth_router.post('/register')
def register(user: UserLogin) -> dict[str, str]:
    """
    Register a new user with AWS Cognito.

    Parameters
    ----------
    user : UserLogin
        The user credentials (username and password) for registration.

    Returns
    -------
    dict
        A response dictionary containing the registration result.

    """
    logger.info('Received register request.')
    return cognito_client.register_user(user.username, user.password)


@auth_router.post('/confirm')
def confirm(user: UserConfirm) -> dict[str, str]:
    """
    Confirm user registration using a confirmation code.

    Parameters
    ----------
    user : UserConfirm
        The username and confirmation code received via email.

    Returns
    -------
    dict
        A response dictionary indicating the confirmation status.

    """
    logger.info('Received confirm request.')
    return cognito_client.confirm_user(user.username, user.confirmation_code)


@auth_router.post('/login')
def login(user: UserLogin) -> dict[str, str]:
    """
    Authenticate a user and return an authentication token.

    Parameters
    ----------
    user : UserLogin
        The user credentials (username and password) for authentication.

    Returns
    -------
    dict
        A response dictionary containing the authentication token.

    """
    logger.info('Received login request.')
    return cognito_client.login_user(user.username, user.password)
