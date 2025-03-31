"""
Module for managing financial reports.

This module provides a service class to generate and retrieve reports using
SQLAlchemy for data retrieval and S3 for storage.

"""
import sqlalchemy as sql

from backend.reports_app.exceptions import InvalidReportType, ReportNotFound
from backend.reports_app.reports_generator import ReportsGenerator, ReportsType
from backend.reports_app.s3client import S3Client


class ReportsService:
    """
    Service for generating and retrieving financial reports.

    Attributes
    ----------
    reports_generator : ReportsGenerator
        Object for generating financial reports based on budget entries.
    s3client : S3Client
        Interface for interacting with S3 storage.

    """

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        """
        Initialize ReportsService.

        Parameters
        ----------
        engine : sql.Engine
            SQLAlchemy database engine for executing queries.

        """
        self.reports_generator = ReportsGenerator(engine)
        self.s3client = S3Client()

    def generate_report(self, report_name: str) -> ReportsType:
        """
        Generate a report and store it in S3.

        Parameters
        ----------
        report_name : str
            The name of the report to generate.

        Returns
        -------
        ReportsType
            The generated report data.

        Raises
        ------
        InvalidReportType
            If the requested report type is not found in ReportsGenerator.

        """
        report_method = getattr(
            self.reports_generator,
            report_name,
            None,
        )
        if report_method is None:
            raise InvalidReportType

        report = report_method()
        self.s3client.save_object(
            remote_path=f'reports/{report_name}.json',
            json_data=report,
        )
        return report

    def get_latest_report(self, report_name: str) -> ReportsType:
        """
        Fetch the latest report from S3.

        Parameters
        ----------
        report_name : str
            The name of the report to retrieve.

        Returns
        -------
        ReportsType
            The latest report data.

        Raises
        ------
        ReportNotFound
            If the report does not exist in S3 storage.

        """
        report = self.s3client.load_object(
            remote_path=f'reports/{report_name}.json',
        )
        if report:
            return report
        raise ReportNotFound
