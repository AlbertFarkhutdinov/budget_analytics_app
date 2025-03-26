from fastapi import APIRouter

from backend.reports_app.reports_service import ReportsService
from backend.entries_app.db_engine import get_engine
from backend.entries_app.models import Base
from custom_logging import config_logging

config_logging()
engine = get_engine()
Base.metadata.create_all(bind=engine)
reports_router = APIRouter()


@reports_router.post(path='/generate/{report_type}')
def generate_report(report_type: str) -> dict[str, dict[str, list[float]]]:
    return ReportsService(engine).generate_report(report_type=report_type)


@reports_router.get(path='/latest/{report_type}')
def get_latest_report(report_type: str) -> dict[str, dict[str, list[float]]]:
    return ReportsService(engine).get_latest_report(report_type=report_type)
