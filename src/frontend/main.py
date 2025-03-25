import streamlit as st

from custom_logging import config_logging
from frontend.apps.auth import AuthPage
from frontend.apps.entries import EntriesPage
from frontend.apps.page_state import PageState


class MainApp:

    def __init__(self):
        self._initialize_session_state()
        self.auth_app = AuthPage()
        self.transactions_page = EntriesPage()

    def run(self) -> None:
        """Run the Streamlit app."""
        self._handle_auth_redirect()
        if st.session_state.page == PageState.entries.value:
            self.transactions_page.run()
        elif st.session_state.page == PageState.auth.value:
            self.auth_app.run()

    @classmethod
    def _initialize_session_state(cls):
        """Initialize Streamlit session state variables."""
        if 'page' not in st.session_state:
            st.session_state.page = PageState.auth.value
        if 'token' not in st.session_state:
            st.session_state.token = ''

    def _handle_auth_redirect(self):
        """Ensure proper navigation based on authentication state."""
        page_state = st.session_state.page
        if st.session_state.token and page_state != PageState.entries.value:
            self._switch_page(PageState.entries.value)
        elif not st.session_state.token and page_state != PageState.auth.value:
            self._switch_page(PageState.auth.value)

    @classmethod
    def _switch_page(cls, page: str) -> None:
        """Switch the current page and trigger a rerun."""
        st.session_state.page = page
        st.rerun()


if __name__ == '__main__':
    config_logging()
    app = MainApp()
    app.run()
