"""
Budget Entries API routes using FastAPI and PostgreSQL.

This module defines endpoints for managing budget entries, including creating,
reading, updating, and deleting entries. It also supports file uploads.

"""
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
    """
    Create a new budget entry in the database.

    Parameters
    ----------
    entry : BudgetEntrySchema
        The budget entry details.

    Returns
    -------
    dict
        A response dictionary indicating the creation status.

    """
    return BudgetService(engine).create_entry(entry=entry)


@entries_router.get(path='/', response_model=list[BudgetEntrySchema])
def read_entries() -> list[BudgetEntry]:
    """
    Return all budget entries from the database.

    Returns
    -------
    list[BudgetEntry]
        A list of budget entries.

    """
    return BudgetService(engine).read_entries()


@entries_router.get(path='/info')
def get_entries_info() -> dict[str, str | int]:
    """
    Return summary information about budget entries.

    Returns
    -------
    dict
        A dictionary containing statistics about the budget entries.

    """
    return BudgetService(engine).get_entries_info()


@entries_router.post(path='/update')
def update_entries(updated_entries: list[BudgetEntrySchema]) -> dict[str, str]:
    """
    Update existing budget entries in the database.

    Parameters
    ----------
    updated_entries : list[BudgetEntrySchema]
        A list of updated budget entries.

    Returns
    -------
    dict
        A response dictionary indicating the update status.

    """
    return BudgetService(engine).update_entries(updated_entries)


@entries_router.post(path='/upload')
def upload_entries(uploaded_file: UploadFile) -> dict[str, str]:
    """
    Process and upload budget entries from a file.

    Parameters
    ----------
    uploaded_file : UploadFile
        The file containing budget entries to be uploaded.

    Returns
    -------
    dict
        A response dictionary indicating the upload status.

    """
    return BudgetService(engine).upload_entries(uploaded_file)


@entries_router.post(path='/clean')
def delete_all_entries() -> dict[str, str]:
    """
    Delete all budget entries from the database.

    Returns
    -------
    dict
        A response dictionary indicating the deletion status.

    """
    return BudgetService(engine).delete_all_entries()
