import logging

import requests
import streamlit as st


class APIClient:
    """Handles API requests."""
    API_BASE_URL = 'http://127.0.0.1:8000'

    @classmethod
    def make_request(
        cls,
        endpoint: str,
        method: str = 'POST',
        data=None,
    ):
        """Unified method for handling API requests."""
        response = requests.request(
            method=method,
            json=data,
            url=f'{cls.API_BASE_URL}{endpoint}',
            headers={'Content-Type': 'application/json'},
        )
        return response.json()

    @classmethod
    def register_user(
        cls,
        username: str,
        password: str,
    ):
        response = cls.make_request(
            endpoint='/auth/register',
            data={
                'username': username,
                'password': password,
            },
        )
        return response

    @classmethod
    def confirm_user(
        cls,
        username: str,
        confirmation_code: str,
    ):
        logger.info(f'confirm_user({username=}, {confirmation_code=})')
        response = cls.make_request(
            endpoint='/auth/confirm',
            data={
                'username': username,
                'confirmation_code': confirmation_code,
            },
        )
        return response

    @classmethod
    def login_user(
        cls,
        username: str,
        password: str,
    ):
        response = cls.make_request(
            endpoint='/auth/login',
            data={'username': username, 'password': password},
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
            logger.info(f'After text input {confirmation_code=})')
            if st.button('Confirm'):
                logger.info(f'After button {confirmation_code=})')
                if not confirmation_code:
                    st.error('Confirmation code cannot be empty.')
                    return
                confirm_response = APIClient.confirm_user(
                    username=self.username,
                    confirmation_code=confirmation_code,
                )
                if 'detail' in confirm_response:
                    st.error(confirm_response['detail'])
                    return
                st.success('User confirmed. You can now log in.')

    def login(self):
        if st.button('Log in'):
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
