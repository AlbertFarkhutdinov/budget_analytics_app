"""
The module that provides the Streamlit page for managing budget entries.

It contains the `EntriesPage` class, which handles the user interface and
logic for managing budget entries, including viewing, adding, saving, deleting,
and uploading budget entries.

"""
import json

import pandas as pd
import streamlit as st

from frontend.api.entries_api_client import EntriesAPIClient
from frontend.apps.base_page import BasePage


class EntriesPage(BasePage):
    """
    A class to handle the UI and logic for managing budget entries.

    Attributes
    ----------
    api : EntriesAPIClient
        API client for budget entries.

    Methods
    -------
    run() -> None
        Run the budget entries page UI.

    """

    def __init__(self) -> None:
        """Initialize the `EntriesPage` instance."""
        self.api = EntriesAPIClient()
        self.entries_info = {}

    def run(self) -> None:
        """
        Run the budget entries page UI.

        Display the budget entries and options for viewing, adding, saving,
        deleting, and uploading entries.

        """
        st.title('Transactions History')
        self.entries_info = self.api.get_entries_info()
        entries_number = self.entries_info.get('entries_number', 0)
        st.write(f'{entries_number} entries in the database.')
        self._view_budget_entries()
        self._add_budget_entry()
        self._upload_csv()

    def _view_budget_entries(self) -> None:
        """Display the budget entries and allow users to make changes."""
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
        """
        Save the changes made to the budget entries.

        This method is triggered when the 'Save Changes' button is pressed.
        It checks that all required fields are filled, then saves the changes.

        Parameters
        ----------
        entries : pd.DataFrame
            The modified budget entries to be saved.

        """
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
        """
        Handle uploading and processing of a CSV file with budget entries.

        This method is triggered when the 'Upload CSV' button is pressed.
        It displays a file uploader for the user to upload a CSV file,
        processes the file, and adds the entries from the file to the database.
        """
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
        """
        Display a form for adding a new budget entry.

        If the user presses the 'Add Budget Entry' button,
        a form is shown with fields for the user to fill out for a new entry.

        """
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
        """
        Delete all budget entries from the database.

        This method is triggered
        when the 'Delete all entries' button is clicked.

        """
        if st.button('Delete all entries'):
            response = self.api.delete_all_entries()
            self._rerun_after_success(response=response)

    @classmethod
    def _check_full_row(
        cls,
        entries: pd.DataFrame,
    ) -> bool:
        """
        Validate all necessary fields in a row.

        This method checks if any required columns have missing
        values and displays an error message if so.

        Parameters
        ----------
        entries : pd.DataFrame
            The budget entries to check.

        Returns
        -------
        bool
            True if all required fields are filled, False otherwise.

        """
        for column in entries.columns:
            if column != 'id' and entries[column].isna().sum():
                st.error(f'Fill "{column}" values')
                return False
        return True

    def _rerun_after_success(self, response: dict[str, str]) -> None:
        """
        Rerun the page after a successful operation.

        This method checks the response and reruns the page
        if the operation was successful, resetting the form visibility.

        Parameters
        ----------
        response : dict
            The response from the API call indicating
            the success or failure of the operation.

        """
        if self.handle_response(response=response) == 1:
            st.session_state.show_form = False
            st.rerun()
