import logging
from io import BytesIO

from frontend.api.api_client import APIClient

logger = logging.getLogger(__name__)


class EntriesAPIClient(APIClient):
    """Handles API requests."""

    def get_budget_entries(self) -> dict[str, str]:
        entries = self.make_request(
            method='GET',
            endpoint='/entries/',
        )
        if entries:
            return entries
        return {}

    def add_budget_entry(
        self,
        entry: dict[str, str | int | None],
    ) -> dict[str, str]:
        """Handle adding a budget entry."""
        response = self.make_request(
            method='POST',
            endpoint='/entries/',
            json_data=entry,
        )
        if response:
            return response
        return {}

    def save_changed_entries(
        self,
        entries: list[dict[str, str | int | None]],
    ) -> dict[str, str]:
        """Handle saving changes budget entries."""
        response = self.make_request(
            method='POST',
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
        """Handle uploading budget entries from CSV."""
        response = self.make_request(
            method='POST',
            endpoint='/entries/upload',
            files=entries_files,
        )
        if response:
            return response
        return {}
