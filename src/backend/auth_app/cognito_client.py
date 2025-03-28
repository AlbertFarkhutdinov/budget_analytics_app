import base64
import hashlib
import hmac
import logging

import boto3

from backend.auth_app import exceptions as auth_exc
from backend.auth_app.settings import AuthSettings

logger = logging.getLogger(__name__)


class CognitoClient:

    def __init__(self, settings: AuthSettings) -> None:
        self.settings = settings
        self.client = boto3.client(
            'cognito-idp',
            region_name=self.settings.cognito_region,
        )

    def register_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info('Received register request.')
        try:
            self.client.sign_up(
                ClientId=self.settings.cognito_client_id,
                SecretHash=self._compute_secret_hash(username),
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
            raise auth_exc.UserAlreadyExistsError from exc
        except Exception as exc:
            raise auth_exc.InternalServerError(
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
                SecretHash=self._compute_secret_hash(username),
            )
        except self.client.exceptions.CodeMismatchException as exc:
            raise auth_exc.InvalidConfirmationCodeError from exc
        except Exception as exc:
            raise auth_exc.InternalServerError(
                detail='Confirmation failed.',
            ) from exc
        return {'message': 'User confirmed. You can now log in.'}

    def login_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info('Received login request.')
        cogn_ex = self.client.exceptions
        exception_map = {
            cogn_ex.UserNotFoundException: auth_exc.UserNotFoundError,
            cogn_ex.NotAuthorizedException: auth_exc.IncorrectCredentialsError,
            cogn_ex.UserNotConfirmedException: auth_exc.UserNotConfirmedError,
        }
        try:
            response = self.client.initiate_auth(
                ClientId=self.settings.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self._compute_secret_hash(username),
                },
            )
        except (
            self.client.exceptions.UserNotFoundException,
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.UserNotConfirmedException,
        ) as exc:
            raise exception_map[type(exc)] from exc
        except Exception as exc:
            detail = 'Login failed.'
            logger.exception(detail)
            raise auth_exc.InternalServerError(detail=detail) from exc
        token = response['AuthenticationResult']['AccessToken']
        return {
            'access_token': token,
        }

    def _compute_secret_hash(self, username: str) -> str:
        if not self.settings.cognito_client_secret:
            raise auth_exc.MissingSecretError
        message = username + str(self.settings.cognito_client_id)
        encoding = 'utf-8'
        dig = hmac.new(
            key=self.settings.cognito_client_secret.encode(encoding),
            msg=message.encode(encoding),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode(encoding)
