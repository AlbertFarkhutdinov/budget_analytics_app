import pandas as pd
import sqlalchemy as sql

from backend.entries_app.models import BudgetEntry
from backend.reports_app.exceptions import InvalidReportType, ReportNotFound
from backend.reports_app.s3client import S3Client


class ReportsService:

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        self.engine = engine
        self.s3client = S3Client()

    def generate_report(
        self,
        report_type: str,
    ) -> dict[str, dict[str, list[float]]]:
        """Generate a report."""
        if report_type == 'mean_expenses_per_day':
            df = (
                self._fetch_data(query=sql.select(BudgetEntry))
                .groupby('date')
                .sum(numeric_only=True)
                .reset_index()
            )
            # TODO replace test report with real calculations
            report = {
                'plot_data': {
                    'x': df.index.values.tolist(),
                    'y': df['amount'].values.tolist(),
                },
            }
        elif report_type == 'category_expenses_per_month':
            # TODO replace test report with real calculations
            report = {
                'plot_data': {
                    'x': [0, 1, 2, 3, 4],
                    'y': [0, 1, 4, 9, 16],
                },
            }
        else:
            raise InvalidReportType

        self.s3client.save_json(
            remote_path=f'reports/{report_type}.json',
            json_data=report,
        )
        return report

    def get_latest_report(
        self,
        report_type: str,
    ) -> dict[str, dict[str, list[float]]]:
        """Fetch the latest report."""
        report = self.s3client.load_json(
            remote_path=f'reports/{report_type}.json',
        )
        if report:
            return report
        raise ReportNotFound

    def _fetch_data(self, query: sql.Select) -> pd.DataFrame:
        """Fetch data from RDS."""
        with self.engine.connect() as connection:
            return pd.read_sql(query, connection)
