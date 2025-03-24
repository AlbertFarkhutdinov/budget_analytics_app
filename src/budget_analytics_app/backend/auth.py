import base64
import hashlib
import hmac
import logging

import boto3
from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from budget_analytics_app.backend import exceptions
from budget_analytics_app.budget_logs import config_logging

logger = logging.getLogger(__name__)
ENCODING = 'utf-8'


class AuthSettings(BaseSettings):
    cognito_user_pool_id: str = ''
    cognito_client_id: str = ''
    cognito_region: str = ''
    cognito_client_secret: str = ''

    model_config = SettingsConfigDict(
        env_file='env/cognito',
        env_file_encoding=ENCODING,
    )


class CognitoClient:

    def __init__(self, settings: AuthSettings) -> None:
        self.settings = settings
        self.client = boto3.client(
            'cognito-idp',
            region_name=self.settings.cognito_region,
        )

    def compute_secret_hash(self, username: str) -> str:
        if not self.settings.cognito_client_secret:
            raise exceptions.MissingSecretError()
        message = username + str(self.settings.cognito_client_id)
        dig = hmac.new(
            key=self.settings.cognito_client_secret.encode(ENCODING),
            msg=message.encode(ENCODING),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode(ENCODING)

    def register_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info('Received register request.')
        try:
            self.client.sign_up(
                ClientId=self.settings.cognito_client_id,
                SecretHash=self.compute_secret_hash(username),
                Username=username,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': username,
                    },
                ],
            )
        except self.client.exceptions.UsernameExistsException as exc:
            raise exceptions.UserAlreadyExistsError() from exc
        except Exception as exc:
            raise exceptions.InternalServerError(
                detail='Registration failed.',
            ) from exc
        return {'message': 'User registered, confirm the email.'}

    def confirm_user(
        self,
        username: str,
        confirmation_code: str,
    ) -> dict[str, str]:
        logger.info('Received confirmation request.')
        try:
            self.client.confirm_sign_up(
                ClientId=self.settings.cognito_client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
                SecretHash=self.compute_secret_hash(username),
            )
        except self.client.exceptions.CodeMismatchException as exc:
            raise exceptions.InvalidConfirmationCodeError() from exc
        except Exception as exc:
            raise exceptions.InternalServerError(
                detail='Confirmation failed.',
            ) from exc
        return {'message': 'User confirmed'}

    def login_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info('Received login request.')
        try:
            response = self.client.initiate_auth(
                ClientId=self.settings.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self.compute_secret_hash(username),
                },
            )
        except self.client.exceptions.UserNotFoundException as exc:
            raise exceptions.UserNotFoundError() from exc
        except self.client.exceptions.NotAuthorizedException as exc:
            raise exceptions.IncorrectCredentialsError() from exc
        except self.client.exceptions.UserNotConfirmedException as exc:
            raise exceptions.UserNotConfirmedError() from exc
        except Exception as exc:
            logger.exception('Login failed.')
            raise exceptions.InternalServerError(
                detail='Login failed.',
            ) from exc
        token = response['AuthenticationResult']['AccessToken']
        return {
            'access_token': token,
        }


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
