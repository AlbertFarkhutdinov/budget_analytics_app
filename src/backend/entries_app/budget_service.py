import sqlalchemy as sql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

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
        with Session(engine) as session:
            for updated_entry in updated_entries:
                stmt = (
                    sql.select(BudgetEntry)
                    .where(BudgetEntry.id.in_([updated_entry.id]))
                    .order_by(BudgetEntry.id)
                )
                try:
                    entry = session.scalars(stmt).one()
                except NoResultFound:
                    entry = BudgetEntry(**updated_entry.model_dump())
                    session.add(entry)
                else:
                    for key, field in updated_entry.model_dump().items():
                        setattr(entry, key, field)
            session.commit()
            return {'message': 'Entries processed successfully.'}
