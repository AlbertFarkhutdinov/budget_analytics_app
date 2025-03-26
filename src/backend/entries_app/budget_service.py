import sqlalchemy as sql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.entries_app.exceptions import ProcessingError
from backend.entries_app.models import BudgetEntry, BudgetEntrySchema


class BudgetService:

    @classmethod
    def create_entry(
        cls,
        engine: sql.Engine,
        entry: BudgetEntrySchema,
    ) -> dict[str, str]:
        with Session(engine) as session:
            db_entry = BudgetEntry(**entry.model_dump(exclude_unset=True))
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
            return {'message': 'Entries processed successfully.'}

    @classmethod
    def read_entries(
        cls,
        engine: sql.Engine,
        skip: int = 0,
        limit: int = 10,
    ) -> list[BudgetEntry]:
        stmt = (
            sql.select(BudgetEntry)
            .order_by(BudgetEntry.date.desc())
            .order_by(BudgetEntry.id.desc())
            .offset(skip)
            .limit(limit)
        )
        with Session(engine) as session:
            return list(session.scalars(stmt))

    @classmethod
    def update_entries(
        cls,
        engine: sql.Engine,
        updated_entries: list[BudgetEntrySchema],
    ) -> dict[str, str]:
        updated_entries = sorted(
            updated_entries,
            key=lambda entry: entry.id,
        )
        entry_ids = [entry.id for entry in updated_entries]
        stmt = (
            sql.select(BudgetEntry)
            .filter(BudgetEntry.id.in_(entry_ids))
            .order_by(BudgetEntry.id)
        )
        with Session(engine) as session:
            entries = list(session.scalars(stmt))
            existing_entries = {
                entry.id: entry
                for entry in entries
            }
            for updated_entry in updated_entries:
                entry = existing_entries.get(updated_entry.id, None)
                if entry is None:
                    new_entry = BudgetEntry(**updated_entry.model_dump())
                    session.add(new_entry)
                else:
                    for key, field in updated_entry.model_dump().items():
                        setattr(entry, key, field)
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ProcessingError from exc
            return {'message': 'Entries processed successfully.'}
