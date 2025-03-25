import streamlit as st

from frontend.api.auth_api_client import AuthAPIClient
from frontend.apps.page_state import PageState


class AuthPage:
    """Handles UI and authentication logic."""

    def __init__(self) -> None:
        self.api = AuthAPIClient()
        self._init_session_state()

    def run(self) -> None:
        """Run the authentication page."""
        st.title('Authentication')

        if st.session_state.token:
            st.success('You are already logged in!')
            if st.button('Logout'):
                self._logout()
            return

        st.header('Login / Register')
        st.session_state.username = st.text_input(
            'Username',
            value=st.session_state.username,
        )

        password = st.text_input('Password', type='password')
        action = st.radio('Choose an action', ('Login', 'Register'))
        if action == 'Register':
            self._register(st.session_state.username, password)
        elif action == 'Login':
            self._login(st.session_state.username, password)

    @classmethod
    def _init_session_state(cls) -> None:
        """Initialize session state variables if they don't exist."""
        if 'username' not in st.session_state:
            st.session_state.username = ''

    def _register(self, username: str, password: str) -> None:
        """Handle user registration and confirmation."""
        if st.button('Create Account'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = self.api.register_user(username, password)
            if self._handle_error(response=response):
                return
            st.success('User registered, confirm the email')

        confirmation_code = st.text_input(
            'Enter confirmation code',
            max_chars=6,
        )
        if st.button('Confirm'):
            if not confirmation_code:
                st.error('Confirmation code cannot be empty.')
                return
            confirm_response = self.api.confirm_user(
                username=username,
                confirmation_code=confirmation_code,
            )
            if not self._handle_error(response=confirm_response):
                st.success('User confirmed. You can now log in.')

    def _login(self, username: str, password: str) -> None:
        """Handle user login."""
        if st.button('Login'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = self.api.login_user(username, password)
            if self._handle_error(response=response):
                return
            token = response.get('access_token', '')
            if token:
                st.session_state.token = token
                st.session_state.page = PageState.entries.value
                st.success('Logged in successfully!')
                st.rerun()

    @classmethod
    def _logout(cls) -> None:
        """Handle user logout."""
        st.session_state.token = None
        st.session_state.username = ''
        st.success('Logged out successfully!')

    @classmethod
    def _handle_error(cls, response: dict[str, str]) -> str:
        detail = response.get('detail', '')
        if detail:
            st.error(detail)
            return detail
        return ''
