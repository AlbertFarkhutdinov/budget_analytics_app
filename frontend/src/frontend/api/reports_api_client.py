"""The module provides an API client for generating and retrieving reports."""

import logging

from frontend.api.api_client import APIClient, ReportsType

logger = logging.getLogger(__name__)


class ReportsAPIClient(APIClient):
    """Handles API requests related to generating and retrieving reports."""

    def generate_report(self, report_type: str) -> ReportsType:
        """
        Generate a report of the specified type.

        Parameters
        ----------
        report_type : str
            The type of report to generate.

        Returns
        -------
        ReportsType
            A dictionary containing the generated report data.

        """
        report = self.make_request(
            method='POST',
            endpoint=f'/reports/generate/{report_type}',
        )
        if report:
            return report
        return {}

    def load_last_report(self, report_type: str) -> ReportsType:
        """
        Load the latest report of the specified type.

        Parameters
        ----------
        report_type : str
            The type of report to retrieve.

        Returns
        -------
        ReportsType
            A dictionary containing the latest report data.

        """
        report = self.make_request(
            method='GET',
            endpoint=f'/reports/latest/{report_type}',
        )
        if report:
            return report
        return {}
