"""
Reports API routes using FastAPI and PostgreSQL.

This module defines endpoints for generating and retrieving reports.

"""
from custom_logging import config_logging
from fastapi import APIRouter

from backend.entries_app.db_engine import get_engine
from backend.entries_app.models import Base
from backend.reports_app.reports_generator import ReportsType
from backend.reports_app.reports_service import ReportsService

config_logging()
engine = get_engine()
Base.metadata.create_all(bind=engine)
reports_router = APIRouter()


@reports_router.post(path='/generate/{report_name}')
def generate_report(report_name: str) -> ReportsType:
    """
    Generate a report based on the specified report name.

    Parameters
    ----------
    report_name : str
        The name of the report to generate.

    Returns
    -------
    ReportsType
        The generated report data.

    """
    return ReportsService(engine).generate_report(report_name=report_name)


@reports_router.get(path='/latest/{report_name}')
def get_latest_report(report_name: str) -> ReportsType:
    """
    Return the latest generated report based on the report name.

    Parameters
    ----------
    report_name : str
        The name of the report to fetch.

    Returns
    -------
    ReportsType
        The latest report data.

    """
    return ReportsService(engine).get_latest_report(report_name=report_name)
