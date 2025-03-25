import streamlit as st

from custom_logging import config_logging
from frontend.api_client import APIClient


class AuthApp:
    """Handles UI and authentication logic."""

    def __init__(self) -> None:
        self.username = ''
        self.password = ''
        self.action = ''

    def register(self) -> None:
        if st.button('Create Account'):
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
                return
            response = APIClient.register_user(self.username, self.password)
            detail = response.get('detail', '')
            if detail:
                st.error(detail)
                return
            st.success('User registered, confirm the email')

        confirmation_code = st.text_input(
            'Enter confirmation code',
            max_chars=6,
        )
        confirm_clicked = st.button('Confirm')
        if confirm_clicked:
            if not confirmation_code:
                st.error('Confirmation code cannot be empty.')
                return
            confirm_response = APIClient.confirm_user(
                username=self.username,
                confirmation_code=confirmation_code,
            )
            detail = confirm_response.get('detail', '')
            if detail:
                st.error(detail)
                return
            st.success('User confirmed. You can now log in.')

    def login(self) -> None:
        login_clicked = st.button('Login')

        if login_clicked:
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
            response = APIClient.login_user(self.username, self.password)
            detail = response.get('detail', '')
            if detail:
                st.error(detail)
            token = response.get('access_token', '')
            if token:
                st.success('Logged in successfully!')
                st.session_state.token = token
                st.session_state.page = 'transactions'
                st.rerun()

    def run(self) -> None:
        st.title('Authentication')
        st.header('Login')
        self.username = st.text_input('Username')
        self.password = st.text_input('Password', type='password')
        self.action = st.radio('Choose an action', ('Login', 'Register'))
        if self.action == 'Register':
            self.register()
        elif self.action == 'Login':
            self.login()


if __name__ == '__main__':
    config_logging()
    AuthApp().run()
