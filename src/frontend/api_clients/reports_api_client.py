import logging

from frontend.api_clients.api_client import APIClient

logger = logging.getLogger(__name__)


class ReportsAPIClient(APIClient):
    """Handles API requests."""
