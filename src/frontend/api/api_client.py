import logging

import requests
import streamlit as st

logger = logging.getLogger(__name__)
API_BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 10
EntryType = dict[str, str | int | None]
ReportType = dict[
    str,
    dict[str, list[float | str]],
]


class APIClient:
    """Handles API requests."""

    @property
    def token(self) -> str:
        return st.session_state.get('token', '')

    def make_request(
        self,
        endpoint: str,
        method: str = 'POST',
        json_data: EntryType | list[EntryType] | None = None,
    ) -> dict[str, str] | ReportType:
        """Unified method for handling API requests."""
        url = f'{API_BASE_URL}{endpoint}'
        headers = {
            **self._get_headers(),
            'Content-Type': 'application/json',
        }
        response = None
        try:
            response = requests.request(
                method=method,
                json=json_data,
                url=url,
                headers=headers,
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            logger.error(f'API request failed: {exc}')  # noqa: TRY400
            try:
                return response.json()
            except AttributeError:
                return {'detail': 'Failed to connect to the server.'}
        return response.json()

    def _get_headers(self) -> dict[str, str]:
        """Return authorization headers if the user is logged in."""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}
