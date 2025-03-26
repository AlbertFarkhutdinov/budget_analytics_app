from fastapi import APIRouter

from backend.entries_app import entries
from custom_logging import config_logging

config_logging()
entries_router = APIRouter()
db = entries.session_local()


@entries_router.get(path='/', response_model=list[entries.BudgetEntrySchema])
def read_entries() -> list[type[entries.BudgetEntry]]:
    return entries.BudgetService.get_entries(db)


@entries_router.post(path='/')
def create_entry(
    entry: entries.BudgetEntrySchema,
) -> entries.BudgetEntrySchema:
    return entries.BudgetService.create_entry(db, entry)


@entries_router.post(path='/update')
def update_entries(
    updated_entries: list[entries.BudgetEntrySchema],
) -> dict[str, str]:
    return entries.BudgetService.update_entries(db, updated_entries)


@entries_router.delete(path='/{entry_id}')
def delete_entry(
    entry_id: int,
) -> dict[str, str]:
    return entries.BudgetService.delete_entry(db, entry_id)
