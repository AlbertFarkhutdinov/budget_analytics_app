"""
Budget Analysis Streamlit App.

This module implements a Streamlit-based budget analysis application.
It provides authentication, expense tracking, and reporting functionality.

"""
import logging

import streamlit as st
from custom_logging import config_logging

from frontend.apps.auth import AuthPage
from frontend.apps.entries import EntriesPage
from frontend.apps.page_state import PageState
from frontend.apps.reports import ReportsPage

logger = logging.getLogger(__name__)
st.set_page_config(
    page_title='Budget Analysis',
)


class MainApp:
    """
    Main application class for the Budget Analysis Streamlit app.

    Attributes
    ----------
    auth_page : AuthPage
        An object to handle the UI and authentication logic.
    entries_page : EntriesPage
        An object to handle the UI and logic for managing budget entries.
    reports_page : ReportsPage
        An object to handle the UI and logic
        for generating and displaying reports.

    Methods
    -------
    run() -> None
        Run the Streamlit app and handle page navigation.

    """

    def __init__(self) -> None:
        """Initialize the main application class."""
        self._initialize_session_state()
        self.auth_page = AuthPage()
        self.entries_page = EntriesPage()
        self.reports_page = ReportsPage()

    def run(self) -> None:
        """Run the Streamlit app and handle page navigation."""
        self._handle_auth_redirect()
        if st.session_state.page == PageState.auth.value:
            self.auth_page.run()
        else:
            self.run_after_login()

    def run_after_login(self) -> None:
        """Display the sidebar menu and handle page selection."""
        sidebar = st.sidebar.radio(
            'Select a page:',
            ['History', 'Reports'],
        )
        if sidebar == 'History':
            st.session_state.page = PageState.entries.value
            self.entries_page.run()
        elif sidebar == 'Reports':
            st.session_state.page = PageState.reports.value
            self.reports_page.run()

    @classmethod
    def _initialize_session_state(cls) -> None:
        """Initialize Streamlit session state variables if not already set."""
        if 'page' not in st.session_state:
            st.session_state.page = PageState.auth.value
        if 'token' not in st.session_state:
            st.session_state.token = ''

    def _handle_auth_redirect(self) -> None:
        """
        Ensure proper navigation based on authentication state.

        Redirect users based on their authentication status
        to the appropriate page.

        """
        page_state = st.session_state.page
        if st.session_state.token and page_state != PageState.entries.value:
            self._switch_page(PageState.entries.value)
        elif not st.session_state.token and page_state != PageState.auth.value:
            self._switch_page(PageState.auth.value)

    @classmethod
    def _switch_page(cls, page: str) -> None:
        """
        Switch the current page and trigger a rerun.

        Parameters
        ----------
        page : str
            The target page state to switch to.

        """
        st.session_state.page = page
        st.rerun()


if __name__ == '__main__':
    config_logging()
    logger.info('Frontend is running.')
    app = MainApp()
    is_with_auth = True
    if is_with_auth:
        app.run()
    else:
        app.run_after_login()  # for tests
