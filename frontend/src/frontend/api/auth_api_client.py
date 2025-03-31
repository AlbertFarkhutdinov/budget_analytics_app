"""The module provides an API client for authentication."""

import logging

from frontend.api.api_client import APIClient

logger = logging.getLogger(__name__)


class AuthAPIClient(APIClient):
    """
    API client for authentication.

    Handles authentication-related API requests,
    including user registration, confirmation, and login.

    """

    def register_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        """
        Register a new user.

        Parameters
        ----------
        username : str
            The username of the user to be registered.
        password : str
            The password for the new user.

        Returns
        -------
        dict
            The API response containing the registration status.

        """
        logger.info('Registering user: %s', username)
        return self.make_request(
            endpoint='/auth/register',
            json_data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )

    def confirm_user(
        self,
        username: str,
        confirmation_code: str,
    ) -> dict[str, str]:
        """
        Confirm a user's registration using a confirmation code.

        Parameters
        ----------
        username : str
            The username of the user to confirm.
        confirmation_code : str
            The confirmation code received by the user.

        Returns
        -------
        dict
            The API response indicating success or failure of confirmation.

        """
        logger.info(
            'Confirming user: %s, code: %s',
            username,
            confirmation_code,
        )
        return self.make_request(
            endpoint='/auth/confirm',
            json_data={
                'username': username.strip(),
                'confirmation_code': confirmation_code.strip(),
            },
        )

    def login_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        """
        Authenticate a user and return a token.

        Parameters
        ----------
        username : str
            The username of the user attempting to log in.
        password : str
            The password of the user attempting to log in.

        Returns
        -------
        dict
            The API response containing authentication status and token.

        """
        logger.info('Logging user: %s', username)
        return self.make_request(
            endpoint='/auth/login',
            json_data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )
