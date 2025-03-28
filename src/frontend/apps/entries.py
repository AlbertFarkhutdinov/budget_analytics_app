import json

import pandas as pd
import streamlit as st

from frontend.api.entries_api_client import EntriesAPIClient
from frontend.apps.base_page import BasePage


class EntriesPage(BasePage):

    def __init__(self) -> None:
        self.api = EntriesAPIClient()
        self.entries_info = {}

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Transactions History')
        self.entries_info = self.api.get_entries_info()
        entries_number = self.entries_info.get('entries_number', 0)
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
            is_full_row = self._check_full_row(entries=entries_df)
            if is_full_row:
                response = self.api.save_changed_entries(
                    entries=json.loads(
                        entries_df.to_json(orient='records'),
                    ),
                )
                self._rerun_after_success(response=response)

    def _upload_csv(self) -> None:
        upload = st.file_uploader(
            'Upload CSV (sep: ";")',
            type=['csv'],
        )
        if upload and 'uploaded_file' not in st.session_state:
            st.session_state['uploaded_file'] = upload
            with st.spinner('Uploading and processing...'):
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
                self._rerun_after_success(response=response)

    def _add_budget_entry(self) -> None:
        """Handle adding a budget entry."""
        if 'show_form' not in st.session_state:
            st.session_state.show_form = False
        if st.button('Add Budget Entry'):
            st.session_state.show_form = True
        if st.session_state.show_form:
            with st.form('budget_entry_form'):
                entry = {
                    'date': st.date_input('Date'),
                    'shop': st.text_input('Shop'),
                    'product': st.text_input('Product'),
                    'amount': st.number_input('Amount'),
                    'category': st.text_input('Category'),
                    'person': st.text_input('Person'),
                    'currency': st.text_input('Currency', value='USD'),
                }
                submit = st.form_submit_button('Submit Entry')
                if submit:
                    entry['date'] = entry['date'].strftime('%Y-%m-%d')
                    response = self.api.add_budget_entry(entry=entry)
                    self._rerun_after_success(response=response)

    def _clean_data(self) -> None:
        if st.button('Delete all entries'):
            response = self.api.delete_all_entries()
            self._rerun_after_success(response=response)

    @classmethod
    def _check_full_row(
        cls,
        entries: pd.DataFrame,
    ) -> bool:
        for column in entries.columns:
            if column != 'id' and entries[column].isna().sum():
                st.error(f'Fill "{column}" values')
                return False
        return True

    def _rerun_after_success(self, response: dict[str, str]) -> None:
        if self._handle_response(response=response) == 1:
            st.session_state.show_form = False
            st.rerun()
