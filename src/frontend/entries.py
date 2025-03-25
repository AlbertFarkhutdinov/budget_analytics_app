import streamlit as st

from custom_logging import config_logging
from frontend.entries_api_client import EntriesAPIClient
from frontend.page_states import PageState


class TransactionsPage:

    def __init__(self) -> None:
        self.api = EntriesAPIClient()
        self.token = st.session_state.get('token', '')
        self.username = st.session_state.get('username', '')
        self.password = ''
        self.confirmation_code = ''

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Budget Analytics')
        self._view_budget_entries()
        self._add_budget_entry()

    def _view_budget_entries(self) -> None:
        """Handle viewing budget entries."""
        st.header('Budget Entries')
        entries = self.api.get_budget_entries()
        if entries:
            st.table(entries)

    def _add_budget_entry(self) -> None:
        """Handle adding a budget entry."""
        if st.button('Add Budget Entry'):
            st.session_state.page = PageState.new_entry.value
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
                response = self.api.add_budget_entry(entry=entry)
                if response:
                    st.success('Entry added successfully')
                    st.session_state.page = PageState.entries.value


if __name__ == '__main__':
    config_logging()
    app = TransactionsPage()
    app.run()
