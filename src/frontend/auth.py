import streamlit as st

from custom_logging import config_logging
from frontend.auth_api_client import AuthAPIClient


class AuthApp:
    """Handles UI and authentication logic."""

    def __init__(self) -> None:
        self.api = AuthAPIClient()
        self.username = ''
        self.password = ''
        self.action = ''

    def run(self) -> None:
        st.title('Authentication')
        st.header('Login')
        self.username = st.text_input('Username')
        self.password = st.text_input('Password', type='password')
        self.action = st.radio('Choose an action', ('Login', 'Register'))
        if self.action == 'Register':
            self._register()
        elif self.action == 'Login':
            self._login()

    def _register(self) -> None:
        if st.button('Create Account'):
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
                return
            response = self.api.register_user(self.username, self.password)
            detail = self._handle_error(response=response)
            if detail:
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
            confirm_response = self.api.confirm_user(
                username=self.username,
                confirmation_code=confirmation_code,
            )
            if not self._handle_error(response=confirm_response):
                st.success('User confirmed. You can now log in.')

    def _login(self) -> None:
        if st.button('Login'):
            if not self.username or not self.password:
                st.error('Username and password cannot be empty.')
            response = self.api.login_user(self.username, self.password)
            self._handle_error(response=response)
            token = response.get('access_token', '')
            if token:
                st.success('Logged in successfully!')
                st.session_state.token = token
                st.session_state.page = 'transactions'
                st.rerun()

    @classmethod
    def _handle_error(cls, response: dict[str, str]) -> str:
        detail = response.get('detail', '')
        if detail:
            st.error(detail)
            return detail
        return ''


if __name__ == '__main__':
    config_logging()
    AuthApp().run()
