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
    url = f'{API_BASE_URL}{endpoint}'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        msg = f'Request failed: {exc}'
        st.error(msg)
        logger.error(msg)
        return {'error': str(exc)}


def register_user(username, password):
    response = make_request(
        method='POST',
        endpoint='/auth/register',
        data={'username': username, 'password': password},
    )
    return response


def confirm_user(username, confirmation_code):
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
    st.title('Authentication App')
    st.header('Login')
    action = st.radio("Choose an action", ('Login', 'Register'))
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if action == 'Register':
        if st.button('Create Account'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = register_user(username, password)
            if 'error' not in response:
                st.success('User registered, confirm the email')
                confirmation_code = st.text_input('Enter confirmation code')
                if st.button('Confirm'):
                    confirm_response = confirm_user(
                        username=username,
                        confirmation_code=confirmation_code,
                    )
                    if 'error' not in confirm_response:
                        st.success('User confirmed. You can now log in.')
                    else:
                        st.error(confirm_response['error'])
            else:
                st.error(response['error'])
    elif action == 'Login':
        if st.button('Log in'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = login_user(username, password)
            if 'access_token' in response:
                st.success('Logged in successfully!')
            else:
                st.error(response.get('error', 'Invalid credentials'))


if __name__ == '__main__':
    run()
