import pandas as pd
import sqlalchemy as sql

from backend.entries_app.settings import DBSettings
from backend.reports_app.exceptions import InvalidReportType, ReportNotFound
from backend.reports_app.s3client import S3Client

db_settings = DBSettings()


DATABASE_URL = sql.URL.create(
    drivername='postgresql',
    username=db_settings.db_user,
    password=db_settings.db_password,
    host=db_settings.db_host,
    port=db_settings.db_port,
    database=db_settings.db_name,
)

engine = sql.create_engine(DATABASE_URL)


class ReportsService:

    def __init__(self) -> None:
        self.s3client = S3Client()

    def generate_report(
        self,
        report_type: str,
    ) -> dict[str, dict[str, list[float]]]:
        """Generate a report."""
        if report_type == 'mean_expenses_per_day':
            # TODO replace test report with real calculations
            report = {
                'plot_data': {
                    'x': [0, 1, 2, 3, 4],
                    'y': [0, 1, 4, 9, 16],
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

    @classmethod
    def _fetch_data(cls, query: str) -> pd.DataFrame:
        """Fetch data from RDS."""
        with engine.connect() as connection:
            return pd.read_sql(query, connection)
