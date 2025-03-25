from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from budget_db_app import entries
from custom_logging import config_logging


def get_db() -> entries.session_local:
    db = entries.session_local()
    try:
        yield db
    finally:
        db.close()


config_logging()
entries_router = APIRouter()


@entries_router.get(path='/', response_model=list[entries.BudgetEntrySchema])
def read_entries(
    db: Session = Depends(get_db),
) -> list[type[entries.BudgetEntry]]:
    return entries.BudgetService.get_entries(db)


@entries_router.post(path='/')
def create_entry(
    entry: entries.BudgetEntrySchema,
    db: Session = Depends(get_db),
) -> entries.BudgetEntrySchema:
    return entries.BudgetService.create_entry(db, entry)


@entries_router.put(
    path='/{entry_id}',
    response_model=entries.BudgetEntrySchema,
)
def update_entry(
    entry_id: int,
    updated_entry: entries.BudgetEntrySchema,
    db: Session = Depends(get_db),
) -> type[entries.BudgetEntry]:
    return entries.BudgetService.update_entry(db, entry_id, updated_entry)


@entries_router.delete(path='/{entry_id}')
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    return entries.BudgetService.delete_entry(db, entry_id)
