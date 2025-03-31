"""
The module that provides the authentication page.

It contains the `AuthPage` class, which handles the authentication logic
and user interface for logging in and registering users.

"""
import streamlit as st

from frontend.api.auth_api_client import AuthAPIClient
from frontend.apps.base_page import BasePage
from frontend.apps.page_state import PageState


class AuthPage(BasePage):
    """
    A class to handle the UI and authentication logic.

    Attributes
    ----------
    api : AuthAPIClient
        API client for authentication.

    Methods
    -------
    run() -> None
        Run the authentication page UI.

    """

    def __init__(self) -> None:
        """Initialize the AuthPage instance."""
        self.api = AuthAPIClient()
        self._init_session_state()

    def run(self) -> None:
        """
        Run the authentication page UI.

        Display the login or registration form,
        depending on the user's action.
        If the user is already logged in, offer the option to log out.

        """
        st.title('Authentication')

        if st.session_state.token:
            st.success('You are already logged in.')
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
        """
        Handle user registration and confirmation flow.

        Display a form for creating a new account and enter the confirmation
        code after registration.

        Parameters
        ----------
        username : str
            The username for the new user.
        password : str
            The password for the new user.

        """
        if st.button('Create Account'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = self.api.register_user(username, password)
            if self.handle_response(response=response) == -1:
                return

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
            self.handle_response(response=confirm_response)

    def _login(self, username: str, password: str) -> None:
        """
        Display a form for logging in with a username and password.

        Parameters
        ----------
        username : str
            The username for the user.
        password : str
            The password for the user.

        """
        if st.button('Login'):
            if not username or not password:
                st.error('Username and password cannot be empty.')
                return
            response = self.api.login_user(username, password)
            if self.handle_response(response=response) == -1:
                return
            token = response.get('access_token', '')
            if token:
                st.session_state.token = token
                st.session_state.page = PageState.entries.value
                st.success('Logged in successfully.')
                st.rerun()

    @classmethod
    def _logout(cls) -> None:
        """Handle user logout and session state cleanup."""
        st.session_state.token = None
        st.session_state.username = ''
        st.success('Logged out successfully.')
