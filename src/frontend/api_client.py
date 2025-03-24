import logging

import requests

logger = logging.getLogger(__name__)
API_BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 10


class APIClient:
    """Handles API requests."""

    @classmethod
    def make_request(
        cls,
        endpoint: str,
        method: str = 'POST',
        json_data: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Unified method for handling API requests."""
        url = f'{API_BASE_URL}{endpoint}'
        response = None
        try:
            response = requests.request(
                method=method,
                json=json_data,
                url=url,
                headers={'Content-Type': 'application/json'},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            logger.exception('API request failed.')
            try:
                return response.json()
            except AttributeError:
                return {'detail': 'Failed to connect to the server.'}

    @classmethod
    def register_user(
        cls,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info(f'Registering user: {username}')
        return cls.make_request(
            endpoint='/auth/register',
            json_data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )

    @classmethod
    def confirm_user(
        cls,
        username: str,
        confirmation_code: str,
    ) -> dict[str, str]:
        logger.info(f'Confirming user: {username}, code: {confirmation_code}')
        return cls.make_request(
            endpoint='/auth/confirm',
            json_data={
                'username': username.strip(),
                'confirmation_code': confirmation_code.strip(),
            },
        )

    @classmethod
    def login_user(
        cls,
        username: str,
        password: str,
    ) -> dict[str, str]:
        logger.info(f'Logging user: {username}')
        return cls.make_request(
            endpoint='/auth/login',
            json_data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )
