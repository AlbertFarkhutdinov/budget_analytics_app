from fastapi import APIRouter

from backend.entries_app.budget_service import BudgetService
from backend.entries_app.db_engine import create_postgres_database, get_engine
from backend.entries_app.models import Base, BudgetEntry, BudgetEntrySchema
from custom_logging import config_logging

config_logging()
create_postgres_database()
engine = get_engine()
Base.metadata.create_all(bind=engine)
entries_router = APIRouter()


@entries_router.get(path='/', response_model=list[BudgetEntrySchema])
def read_entries() -> list[type[BudgetEntry]]:
    return BudgetService.get_entries(engine)


@entries_router.post(path='/')
def create_entry(
    entry: BudgetEntrySchema,
) -> dict[str, str]:
    return BudgetService.create_entry(
        engine=engine,
        entry=entry,
    )


@entries_router.post(path='/update')
def update_entries(
    updated_entries: list[BudgetEntrySchema],
) -> dict[str, str]:
    return BudgetService.update_entries(
        engine=engine,
        updated_entries=updated_entries,
    )
