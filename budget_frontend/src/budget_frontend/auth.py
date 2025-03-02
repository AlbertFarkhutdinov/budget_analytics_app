import logging

import requests
import streamlit as st


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


API_BASE_URL = 'http://127.0.0.1:8000'


def make_request(method, endpoint, data=None):
    """Unified method for handling API requests."""
    response = requests.request(
        method=method,
        json=data,
        url=f'{API_BASE_URL}{endpoint}',
        headers={'Content-Type': 'application/json'},
    )
    return response.json()


def register_user(username, password):
    response = make_request(
        method='POST',
        endpoint='/auth/register',
        data={'username': username, 'password': password},
    )
    return response


def confirm_user(username, confirmation_code):
    logger.info(f'confirm_user({username=}, {confirmation_code=})')
    response = make_request(
        method='POST',
        endpoint='/auth/confirm',
        data={'username': username, 'confirmation_code': confirmation_code},
    )
    return response


def login_user(username, password):
    response = make_request(
        method='POST',
        endpoint='/auth/login',
        data={'username': username, 'password': password},
    )
    return response


def run():
    st.title('Authentication')
    st.header('Login')
    action = st.radio("Choose an action", ('Login', 'Register'))
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if action == 'Register':
        if st.button('Create Account'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            register_response = register_user(username, password)
            if 'detail' in register_response:
                st.error(register_response['detail'])
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
                confirm_response = confirm_user(
                    username=username,
                    confirmation_code=confirmation_code,
                )
                if 'detail' in confirm_response:
                    st.error(confirm_response['detail'])
                    return
                st.success('User confirmed. You can now log in.')
    elif action == 'Login':
        if st.button('Log in'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            login_response = login_user(username, password)
            print(f'{login_response = }')
            if 'detail' in login_response:
                st.error(login_response['detail'])
                return
            st.success('Logged in successfully!')


if __name__ == '__main__':
    run()
