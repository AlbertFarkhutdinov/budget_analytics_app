import logging

import requests
import streamlit as st


class APIClient:
    """Handles API requests."""
    API_BASE_URL = 'http://127.0.0.1:8000'
    TIMEOUT = 10

    @classmethod
    def make_request(
        cls,
        endpoint: str,
        method: str = 'POST',
        data=None,
    ):
        """Unified method for handling API requests."""
        url = f'{cls.API_BASE_URL}{endpoint}'
        response = None
        try:
            response = requests.request(
                method=method,
                json=data,
                url=url,
                headers={'Content-Type': 'application/json'},
                timeout=cls.TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logging.error(f'API request failed: {exc}')
            try:
                return response.json()
            except AttributeError:
                return {'detail': 'Failed to connect to the server.'}

    @classmethod
    def register_user(
        cls,
        username: str,
        password: str,
    ):
        logging.info(f'Registering user: {username}')
        response = cls.make_request(
            endpoint='/auth/register',
            data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )
        return response

    @classmethod
    def confirm_user(
        cls,
        username: str,
        password: str,
        confirmation_code: str,
    ):
        logging.info(f'Confirming user: {username}, code: {confirmation_code}')
        response = cls.make_request(
            endpoint='/auth/confirm',
            data={
                'username': username.strip(),
                'password': password.strip(),
                'confirmation_code': confirmation_code.strip(),
            },
        )
        return response

    @classmethod
    def login_user(
        cls,
        username: str,
        password: str,
    ):
        logging.info(f'Logging user: {username}')
        response = cls.make_request(
            endpoint='/auth/login',
            data={
                'username': username.strip(),
                'password': password.strip(),
            },
        )
        return response


class AuthApp:
    """Handles UI and authentication logic."""

    def __init__(self):
        st.title('Authentication')
        st.header('Login')
        self.username = st.text_input('Username')
        self.password = st.text_input('Password', type='password')
        self.action = st.radio("Choose an action", ('Login', 'Register'))

    def register(self):
        if st.button('Create Account'):
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
                return
            response = APIClient.register_user(self.username, self.password)
            if 'detail' in response:
                st.error(response['detail'])
                return
            st.success('User registered, confirm the email')

        confirmation_code = st.text_input(
            'Enter confirmation code',
            max_chars=6,
        )
        logging.info(f'After text input {confirmation_code=})')
        confirm_clicked = st.button('Confirm')
        if confirm_clicked:
            logging.info(f'After button {confirmation_code=})')
            if not confirmation_code:
                st.error('Confirmation code cannot be empty.')
                return
            confirm_response = APIClient.confirm_user(
                username=self.username,
                password=self.password,
                confirmation_code=confirmation_code,
            )
            if 'detail' in confirm_response:
                st.error(confirm_response['detail'])
                return
            st.success('User confirmed. You can now log in.')

    def login(self):
        login_clicked = st.button('Login')
        if login_clicked:
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
                return
            response = APIClient.login_user(self.username, self.password)
            if 'detail' in response:
                st.error(response['detail'])
                return
            st.success('Logged in successfully!')

    def run(self):
        if self.action == 'Register':
            self.register()
        elif self.action == 'Login':
            self.login()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    AuthApp().run()
