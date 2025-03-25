import logging

from frontend.api.api_client import APIClient

logger = logging.getLogger(__name__)


class AuthAPIClient(APIClient):
    """Handles API requests."""

    def register_user(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
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
        logger.info('Logging user: %s', username)
        return self.make_request(
            endpoint='/auth/login',
            json_data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )
