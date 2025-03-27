import logging
from io import BytesIO

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
        files: dict[str, tuple[str, BytesIO, str]] | None = None,
    ) -> dict[str, str] | ReportType:
        """Unified method for handling API requests."""
        url = f'{API_BASE_URL}{endpoint}'

        response = None
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': {**self._get_headers()},
        }
        if files is None and json_data is not None:
            request_kwargs['json'] = json_data
        elif files is not None:
            request_kwargs['files'] = files
        try:
            response = requests.request(
                **request_kwargs,
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            logger.error('API request failed: %s', str(exc))  # noqa: TRY400
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
