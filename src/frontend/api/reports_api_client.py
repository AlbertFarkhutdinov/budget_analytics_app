import logging

from frontend.api.api_client import APIClient

logger = logging.getLogger(__name__)


class ReportsAPIClient(APIClient):
    """Handles API requests."""
