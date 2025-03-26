import logging

from frontend.api.api_client import APIClient, ReportType

logger = logging.getLogger(__name__)


class ReportsAPIClient(APIClient):
    """Handles API requests."""

    def generate_report(self, report_type: str) -> ReportType:
        report = self.make_request(
            method='POST',
            endpoint=f'/reports/generate/{report_type}',
        )
        if report:
            return report
        return {}

    def load_last_report(self, report_type: str) -> ReportType:
        report = self.make_request(
            method='GET',
            endpoint=f'/reports/latest/{report_type}',
        )
        if report:
            return report
        return {}
