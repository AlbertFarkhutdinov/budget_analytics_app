import streamlit as st

from custom_logging import config_logging
from frontend.auth import AuthApp
from frontend.entries import TransactionsPage


class MainApp:

    def __init__(self):
        if 'page' not in st.session_state:
            st.session_state.page = 'auth'
        if 'token' not in st.session_state:
            st.session_state.token = ''
        self.auth_app = AuthApp()
        self.transactions_page = TransactionsPage()

    def run(self) -> None:
        """Run the Streamlit app."""
        if st.session_state.token and st.session_state.page != 'transactions':
            self._switch_page('transactions')
        elif not st.session_state.token and st.session_state.page != 'auth':
            self._switch_page('auth')

        if st.session_state.page.startswith('transactions'):
            self.transactions_page.run()
        elif st.session_state.page == 'auth':
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
