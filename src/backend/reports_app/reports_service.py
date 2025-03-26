import sqlalchemy as sql

from backend.reports_app.exceptions import InvalidReportType, ReportNotFound
from backend.reports_app.reports_generator import ReportsGenerator, ReportType
from backend.reports_app.s3client import S3Client


class ReportsService:

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        self.reports_generator = ReportsGenerator(engine)
        self.s3client = S3Client()

    def generate_report(self, report_name: str) -> ReportType:
        """Generate a report."""
        report_method = getattr(
            self.reports_generator,
            report_name,
            None,
        )
        if report_method is None:
            raise InvalidReportType

        report = report_method()
        self.s3client.save_json(
            remote_path=f'reports/{report_name}.json',
            json_data=report,
        )
        return report

    def get_latest_report(self, report_name: str) -> ReportType:
        """Fetch the latest report."""
        report = self.s3client.load_json(
            remote_path=f'reports/{report_name}.json',
        )
        if report:
            return report
        raise ReportNotFound
