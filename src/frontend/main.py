import logging

import streamlit as st

from custom_logging import config_logging
from frontend.auth import AuthApp
from frontend.entries import TransactionsPage

logger = logging.getLogger(__name__)
API_BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 10


class MainApp:

    @property
    def page(self) -> str:
        return st.session_state.get('page', 'transactions')

    @property
    def token(self) -> str:
        return st.session_state.get('token', '')

    def run(self) -> None:
        """Run the Streamlit app."""
        if self.token:
            st.session_state.page = 'transactions'
        else:
            st.session_state.page = 'auth'

        if self.page.startswith('transactions'):
            transactions_page = TransactionsPage()
            transactions_page.run()
        elif self.page == 'auth':
            auth_app = AuthApp()
            auth_app.run()


if __name__ == '__main__':
    config_logging()
    app = MainApp()
    app.run()
