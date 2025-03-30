"""
The module provides an API client for interacting with a backend server.

It includes functionality for making authenticated API requests
and handling responses.

"""

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
ReportsType = dict[str, ReportType]


class APIClient:
    """Handles API requests, including authentication and error handling."""

    @property
    def token(self) -> str:
        """
        Return the authentication token from Streamlit session state.

        Returns
        -------
        str
            The authentication token if available, otherwise an empty string.

        """
        return st.session_state.get('token', '')

    def make_request(
        self,
        endpoint: str,
        method: str = 'POST',
        json_data: EntryType | list[EntryType] | None = None,
        files: dict[str, tuple[str, BytesIO, str]] | None = None,
    ) -> dict[str, str | int] | ReportsType:
        """
        Send a request to API and return a response.

        Parameters
        ----------
        endpoint : str
            The API endpoint to call.
        method : str, optional
            The HTTP method to use (default is 'POST').
        json_data : EntryType or list of EntryType, optional
            JSON object to send with the request.
        files : dict, optional
            Files to upload.

        Returns
        -------
        dict or ReportsType
            The JSON response from the server, or an error message.

        """
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
            logger.error('API request failed: %s', str(exc))
        try:
            return response.json()
        except AttributeError:
            return {'detail': 'Failed to connect to the server.'}
        except requests.exceptions.JSONDecodeError:
            return {'detail': 'Failed to decode response.'}

    def _get_headers(self) -> dict[str, str]:
        """
        Return authorization headers if the user is logged in.

        Returns
        -------
        dict
            A dictionary containing the authorization header
            if the user is authenticated.

        """
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}
