"""
Module for handling authentication with AWS Cognito.

This module provides a `CognitoClient` class
that interacts with AWS Cognito for user registration,
confirmation, and login functionality.

"""

import base64
import hashlib
import hmac
import logging

import boto3

from backend.auth_app import exceptions as auth_exc
from backend.auth_app.settings import AuthSettings

logger = logging.getLogger(__name__)


class CognitoClient:
    """
    Client for interacting with AWS Cognito.

    This class provides methods to register, confirm,
    and authenticate users with AWS Cognito.

    """

    def __init__(self, settings: AuthSettings) -> None:
        """
        Initialize the CognitoClient.

        Parameters
        ----------
        settings : AuthSettings
            Configuration settings for Cognito authentication.

        """
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
        """
        Register a new user in Cognito.

        Parameters
        ----------
        username : str
            The email address of the user.
        password : str
            The password for the user account.

        Returns
        -------
        dict
            A message indicating that the user needs to confirm their email.

        Raises
        ------
        UserAlreadyExistsError
            If the user already exists.
        InternalServerError
            If registration fails due to an unexpected error.

        """
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
        """
        Confirm a user's email address.

        Parameters
        ----------
        username : str
            The email address of the user.
        confirmation_code : str
            The confirmation code received via email.

        Returns
        -------
        dict
            A message indicating successful confirmation.

        Raises
        ------
        InvalidConfirmationCodeError
            If the provided confirmation code is invalid.
        InternalServerError
            If confirmation fails due to an unexpected error.

        """
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
        """
        Authenticate a user and return an access token.

        Parameters
        ----------
        username : str
            The email address of the user.
        password : str
            The password for the user account.

        Returns
        -------
        dict
            A dictionary containing the access token.

        Raises
        ------
        UserNotFoundError
            If the user does not exist.
        IncorrectCredentialsError
            If the credentials are incorrect.
        UserNotConfirmedError
            If the user has not confirmed their email.
        InternalServerError
            If login fails due to an unexpected error.

        """
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
        """
        Compute the secret hash for AWS Cognito authentication.

        Parameters
        ----------
        username : str
            The email address of the user.

        Returns
        -------
        str
            The computed secret hash.

        Raises
        ------
        MissingSecretError
            If the client secret is missing in the settings.

        """
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
