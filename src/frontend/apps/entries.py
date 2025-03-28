import json

import pandas as pd
import streamlit as st

from frontend.api.entries_api_client import EntriesAPIClient
from frontend.apps.base_page import BasePage


class EntriesPage(BasePage):

    def __init__(self) -> None:
        self.api = EntriesAPIClient()
        self.info = {}

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Transactions History')
        self.info = self.api.get_entries_info()
        entries_number = self.info.get('entries_number', 0)
        st.write(f'{entries_number} entries in the database.')
        self._view_budget_entries()
        self._add_budget_entry()
        self._upload_csv()

    def _view_budget_entries(self) -> None:
        """Handle viewing budget entries."""
        entries = self.api.get_budget_entries()
        if entries:
            entries_table = st.data_editor(
                entries,
                column_config={'id': None},
                num_rows='dynamic',
            )
            self._save_changes(entries=entries_table)
            self._clean_data()

    def _save_changes(self, entries: pd.DataFrame) -> None:
        if st.button('Save Changes'):
            entries_df = pd.DataFrame(entries)
            for column in entries_df.columns:
                if column != 'id' and entries_df[column].isna().sum():
                    st.error(f'Fill "{column}" values')
                    break
            else:
                response = self.api.save_changed_entries(
                    entries=json.loads(
                        entries_df.to_json(orient='records'),
                    ),
                )
                if self._handle_response(response=response) == 1:
                    st.rerun()

    def _upload_csv(self) -> None:
        upload = st.file_uploader(
            'Upload CSV (sep: ";")',
            type=['csv'],
        )
        if upload:
            with st.spinner('Uploading and processing...'):
                with upload:
                    entries_files = {
                        'uploaded_file': (
                            upload.name,
                            upload.read(),
                            'text/csv',
                        ),
                    }
                    response = self.api.upload_entries_from_csv(
                        entries_files=entries_files,
                    )
                if self._handle_response(response=response) == 1:
                    st.rerun()

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
                    if self._handle_response(response=response) == 1:
                        st.session_state.show_form = False
                        st.rerun()

    def _clean_data(self) -> None:
        if st.button('Delete all entries'):
            response = self.api.delete_all_entries()
            if self._handle_response(response=response) == 1:
                st.rerun()
