from fastapi import APIRouter

from backend.reports_app.reports_service import ReportsService
from custom_logging import config_logging

config_logging()
reports_router = APIRouter()


@reports_router.post(path='/generate/{report_type}')
def generate_report(report_type: str) -> dict[str, dict[str, list[float]]]:
    return ReportsService().generate_report(report_type=report_type)


@reports_router.get(path='/latest/{report_type}')
def get_latest_report(report_type: str) -> dict[str, dict[str, list[float]]]:
    return ReportsService().get_latest_report(report_type=report_type)
