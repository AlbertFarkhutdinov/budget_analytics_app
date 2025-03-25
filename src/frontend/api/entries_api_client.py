import logging

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
