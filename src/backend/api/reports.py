from fastapi import APIRouter

from backend.entries_app.db_engine import get_engine
from backend.entries_app.models import Base
from backend.reports_app.reports_generator import ReportType
from backend.reports_app.reports_service import ReportsService
from custom_logging import config_logging

config_logging()
engine = get_engine()
Base.metadata.create_all(bind=engine)
reports_router = APIRouter()


@reports_router.post(path='/generate/{report_name}')
def generate_report(report_name: str) -> ReportType:
    return ReportsService(engine).generate_report(report_name=report_name)


@reports_router.get(path='/latest/{report_name}')
def get_latest_report(report_name: str) -> ReportType:
    return ReportsService(engine).get_latest_report(report_name=report_name)
