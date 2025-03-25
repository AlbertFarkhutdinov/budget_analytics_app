import streamlit as st

from frontend.api_clients.entries_api_client import EntriesAPIClient


class EntriesPage:

    def __init__(self) -> None:
        self.api = EntriesAPIClient()

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Transactions History')
        self._view_budget_entries()
        self._add_budget_entry()

    def _view_budget_entries(self) -> None:
        """Handle viewing budget entries."""
        entries = self.api.get_budget_entries()
        if entries:
            st.data_editor(
                entries,
                column_config={
                    'id': None,
                },
                num_rows='dynamic',
            )

    def _add_budget_entry(self) -> None:
        """Handle adding a budget entry."""
        if 'show_form' not in st.session_state:
            st.session_state.show_form = False

        if st.button('Add Budget Entry'):
            st.session_state.show_form = True

        if st.session_state.show_form:
            with st.form('budget_entry_form'):
                date = st.date_input('Date')
                shop = st.text_input('Shop')
                product = st.text_input('Product')
                amount = st.number_input('Amount')
                category = st.text_input('Category')
                person = st.text_input('Person')
                currency = st.text_input('Currency', value='USD')

                submit = st.form_submit_button('Submit Entry')
                if submit:
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
                        st.session_state.show_form = False
                        st.rerun()
