import base64
import hashlib
import hmac
import logging

import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from budget_analytics_app.budget_logs import config_logging

logger = logging.getLogger(__name__)


class AuthSettings(BaseSettings):
    COGNITO_USER_POOL_ID: str = ''
    COGNITO_CLIENT_ID: str = ''
    COGNITO_REGION: str = ''
    COGNITO_CLIENT_SECRET: str = ''

    model_config = SettingsConfigDict(
        env_file='env/cognito',
        env_file_encoding='utf-8',
    )


class CognitoClient:

    def __init__(self, settings: AuthSettings) -> None:
        self.settings = settings
        self.client = boto3.client(
            'cognito-idp',
            region_name=self.settings.COGNITO_REGION,
        )

    def compute_secret_hash(self, username: str) -> str:
        if not self.settings.COGNITO_CLIENT_SECRET:
            raise ValueError('COGNITO_CLIENT_SECRET is missing.')
        message = username + str(self.settings.COGNITO_CLIENT_ID)
        dig = hmac.new(
            key=self.settings.COGNITO_CLIENT_SECRET.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode('utf-8')

    def register_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str] | None:
        logger.info(f'Registering user: {username}')
        try:
            self.client.sign_up(
                ClientId=self.settings.COGNITO_CLIENT_ID,
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
            raise HTTPException(
                status_code=400,
                detail='User already exists',
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc
        else:
            return {'message': 'User registered, confirm the email.'}

    def confirm_user(
        self,
        username: str,
        confirmation_code: str,
    ) -> dict[str, str] | None:
        logger.info(f'Confirming user: {username}, code: {confirmation_code}')
        try:
            self.client.confirm_sign_up(
                ClientId=self.settings.COGNITO_CLIENT_ID,
                Username=username,
                ConfirmationCode=confirmation_code,
                SecretHash=self.compute_secret_hash(username),
            )
        except self.client.exceptions.CodeMismatchException as exc:
            raise HTTPException(
                status_code=400,
                detail='Invalid confirmation code',
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc
        else:
            return {'message': 'User confirmed'}

    def login_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str] | None:
        logger.info(f'Logging user: {username}')
        try:
            response = self.client.initiate_auth(
                ClientId=self.settings.COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self.compute_secret_hash(username),
                },
            )
        except self.client.exceptions.UserNotFoundException as exc:
            raise HTTPException(
                status_code=400,
                detail='User not found',
            ) from exc
        except self.client.exceptions.NotAuthorizedException as exc:
            raise HTTPException(
                status_code=401,
                detail='Incorrect username or password',
            ) from exc
        except self.client.exceptions.UserNotConfirmedException as exc:
            raise HTTPException(
                status_code=403,
                detail='User is not confirmed.',
            ) from exc
        except Exception as exc:
            logger.exception('Login failed.')
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc
        else:
            token = response['AuthenticationResult']['AccessToken']
            return {
                'access_token': token,
            }


class User(BaseModel):
    username: str
    password: str
    confirmation_code: str = ''


config_logging()
settings = AuthSettings()
cognito_client = CognitoClient(settings)
auth_router = APIRouter()


@auth_router.post('/register')
def register(user: User) -> dict[str, str] | None:
    logger.info(f'Received register request for {user.username}')
    return cognito_client.register_user(user.username, user.password)


@auth_router.post('/confirm')
def confirm(user: User) -> dict[str, str] | None:
    logger.info(f'Received confirm request for {user.username}')
    return cognito_client.confirm_user(user.username, user.confirmation_code)


@auth_router.post('/login')
def login(user: User) -> dict[str, str] | None:
    logger.info(f'Received login request for {user.username}')
    return cognito_client.login_user(user.username, user.password)
