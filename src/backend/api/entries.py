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


@entries_router.put(
    path='/{entry_id}',
    response_model=entries.BudgetEntrySchema,
)
def update_entry(
    entry_id: int,
    updated_entry: entries.BudgetEntrySchema,
) -> type[entries.BudgetEntry]:
    return entries.BudgetService.update_entry(db, entry_id, updated_entry)


@entries_router.delete(path='/{entry_id}')
def delete_entry(
    entry_id: int,
) -> dict[str, str]:
    return entries.BudgetService.delete_entry(db, entry_id)
