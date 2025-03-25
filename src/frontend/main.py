import streamlit as st

from custom_logging import config_logging
from frontend.auth import AuthApp
from frontend.entries import TransactionsPage
from frontend.page_states import PageState


class MainApp:

    def __init__(self):
        if 'page' not in st.session_state:
            st.session_state.page = PageState.auth.value
        if 'token' not in st.session_state:
            st.session_state.token = ''
        self.auth_app = AuthApp()
        self.transactions_page = TransactionsPage()

    def run(self) -> None:
        """Run the Streamlit app."""
        page_state = st.session_state.page
        if st.session_state.token and page_state != PageState.entries.value:
            self._switch_page(PageState.entries.value)
        elif not st.session_state.token and page_state != PageState.auth.value:
            self._switch_page(PageState.auth.value)

        entry_pages = {
            PageState.entries.value,
            PageState.new_entry.value,
        }
        if st.session_state.page in entry_pages:
            self.transactions_page.run()
        elif st.session_state.page == PageState.auth.value:
            self.auth_app.run()

    @classmethod
    def _switch_page(cls, page: str) -> None:
        """Switch the current page and trigger a rerun."""
        st.session_state.page = page
        st.rerun()


if __name__ == '__main__':
    config_logging()
    app = MainApp()
    app.run()
