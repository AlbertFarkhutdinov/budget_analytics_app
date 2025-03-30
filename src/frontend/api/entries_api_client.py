"""The module provides an API client for managing budget entries."""

import logging
from io import BytesIO

from frontend.api.api_client import APIClient

logger = logging.getLogger(__name__)


class EntriesAPIClient(APIClient):
    """Handles API requests related to budget entries."""

    def get_budget_entries(self) -> dict[str, str]:
        """
        Return all budget entries.

        Returns
        -------
        dict
            A dictionary containing budget entries.

        """
        entries = self.make_request(
            method='GET',
            endpoint='/entries/',
        )
        if entries:
            return entries
        return {}

    def get_entries_info(self) -> dict[str, str | int]:
        """
        Return summary information about budget entries.

        Returns
        -------
        dict
            A dictionary containing summary details.

        """
        entries = self.make_request(
            method='GET',
            endpoint='/entries/info',
        )
        if entries:
            return entries
        return {}

    def add_budget_entry(
        self,
        entry: dict[str, str | int | None],
    ) -> dict[str, str]:
        """
        Add a new budget entry.

        Parameters
        ----------
        entry : dict
            A dictionary containing entry details.

        Returns
        -------
        dict
            The API response confirming the entry creation.

        """
        response = self.make_request(
            endpoint='/entries/create',
            json_data=entry,
        )
        if response:
            return response
        return {}

    def save_changed_entries(
        self,
        entries: list[dict[str, str | int | None]],
    ) -> dict[str, str]:
        """
        Save updates to multiple budget entries.

        Parameters
        ----------
        entries : list of dict
            A list of dictionaries containing updated budget entries.

        Returns
        -------
        dict
            The API response confirming the updates.

        """
        response = self.make_request(
            endpoint='/entries/update',
            json_data=entries,
        )
        if response:
            return response
        return {}

    def upload_entries_from_csv(
        self,
        entries_files: dict[str, tuple[str, BytesIO, str]],
    ) -> dict[str, str]:
        """
        Upload budget entries from a CSV file.

        Parameters
        ----------
        entries_files : dict
            A dictionary where keys are filenames and values are file tuples
            (filename, file object, MIME type).

        Returns
        -------
        dict
            The API response confirming the upload.

        """
        response = self.make_request(
            endpoint='/entries/upload',
            files=entries_files,
        )
        if response:
            return response
        return {}

    def delete_all_entries(self) -> dict[str, str]:
        """
        Delete all budget entries.

        Returns
        -------
        dict
            The API response confirming deletion.

        """
        response = self.make_request(
            endpoint='/entries/clean',
        )
        if response:
            return response
        return {}
