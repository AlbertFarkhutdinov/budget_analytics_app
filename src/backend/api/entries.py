from fastapi import APIRouter, UploadFile

from backend.entries_app.budget_service import BudgetService
from backend.entries_app.db_engine import create_postgres_database, get_engine
from backend.entries_app.models import Base, BudgetEntry, BudgetEntrySchema
from custom_logging import config_logging

config_logging()
create_postgres_database()
engine = get_engine()
Base.metadata.create_all(bind=engine)
entries_router = APIRouter()


@entries_router.post(path='/create')
def create_entry(entry: BudgetEntrySchema) -> dict[str, str]:
    return BudgetService(engine).create_entry(entry=entry)


@entries_router.get(path='/', response_model=list[BudgetEntrySchema])
def read_entries() -> list[BudgetEntry]:
    return BudgetService(engine).read_entries()


@entries_router.get(path='/info')
def get_entries_info() -> dict[str, str | int]:
    return BudgetService(engine).get_entries_info()


@entries_router.post(path='/update')
def update_entries(updated_entries: list[BudgetEntrySchema]) -> dict[str, str]:
    return BudgetService(engine).update_entries(updated_entries)


@entries_router.post(path='/upload')
def upload_entries(uploaded_file: UploadFile) -> dict[str, str]:
    return BudgetService(engine).upload_entries(uploaded_file)


@entries_router.post(path='/clean')
def delete_all_entries() -> dict[str, str]:
    return BudgetService(engine).delete_all_entries()
