import logging

import requests
import streamlit as st

from custom_logging import config_logging
from frontend.auth import AuthApp

logger = logging.getLogger(__name__)
API_BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 10


class BudgetAnalyticsApp:

    def __init__(self) -> None:
        self.token = st.session_state.get('token', '')
        self.username = st.session_state.get('username', '')
        self.password = ''
        self.confirmation_code = ''

    def get_headers(self) -> dict[str, str]:
        """Return authorization headers if the user is logged in."""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    def add_budget_entry(self) -> None:
        """Handle adding a budget entry."""
        st.header('Add Budget Entry')
        date = st.date_input('Date')
        shop = st.text_input('Shop')
        product = st.text_input('Product')
        amount = st.number_input('Amount', min_value=0)
        category = st.text_input('Category')
        person = st.text_input('Person')
        currency = st.text_input('Currency', value='USD')

        if st.button('Submit Entry'):
            entry = {
                'date': date.strftime('%Y-%m-%d'),
                'shop': shop,
                'product': product,
                'amount': amount,
                'category': category,
                'person': person,
                'currency': currency,
            }
            response = self._make_request(
                method='POST',
                endpoint='/entries/',
                json_data=entry,
            )
            if response:
                st.success('Entry added successfully')

    def view_budget_entries(self) -> None:
        """Handle viewing budget entries."""
        st.header('Budget Entries')
        if st.button('Load Entries'):
            entries = self._make_request(
                method='GET',
                endpoint='/entries/',
            )
            if entries:
                st.table(entries)

    def run(self) -> None:
        """Run the Streamlit app."""
        if not self.token:
            auth_app = AuthApp()
            auth_app.run()
            self.token = auth_app.token
            st.session_state['token'] = self.token
        if self.token:
            st.title('Budget Analytics')
            self.add_budget_entry()
            self.view_budget_entries()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, str | int | None] | None = None,
    ) -> dict[str, str] | None:
        """Unified method for handling API requests."""
        url = f'{API_BASE_URL}{endpoint}'
        headers = {**self.get_headers(), 'Content-Type': 'application/json'}

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_data,
                headers=headers,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            msg = f'Request failed: {exc}'
            st.error(msg)
            logger.exception(msg)
            return None


if __name__ == '__main__':
    config_logging()
    app = BudgetAnalyticsApp()
    app.run()
