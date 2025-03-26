from datetime import UTC, datetime

import sqlalchemy as sql
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from backend.entries_app.exceptions import EntryNotFound, ProcessingError
from backend.entries_app.settings import DBSettings

db_settings = DBSettings()


DATABASE_URL = URL.create(
    drivername='postgresql',
    username=db_settings.db_user,
    password=db_settings.db_password,
    host=db_settings.db_host,
    port=db_settings.db_port,
    database=db_settings.db_name,
)

engine = sql.create_engine(DATABASE_URL)
session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


class BudgetEntry(Base):
    __tablename__ = 'budget_entries'
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    date = sql.Column(sql.DateTime, default=datetime.now(UTC))
    shop = sql.Column(sql.String, index=True)
    product = sql.Column(sql.String)
    amount = sql.Column(sql.Float)
    category = sql.Column(sql.String)
    person = sql.Column(sql.String)
    currency = sql.Column(sql.String)


class BudgetEntrySchema(BaseModel):
    id: int | None = None
    date: datetime
    shop: str
    product: str
    amount: float
    category: str
    person: str
    currency: str

    class Config:
        from_attributes = True


def create_database() -> None:
    temp_engine = sql.create_engine(
        URL.create(
            drivername='postgresql',
            username=db_settings.db_user,
            password=db_settings.db_password,
            host=db_settings.db_host,
            port=db_settings.db_port,
            database='postgres',
        ),
    )
    with temp_engine.connect() as conn:
        conn.execute(sql.text('COMMIT'))
        sql_query = text(
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_database WHERE datname = :db_name
                ) THEN
                    EXECUTE format('CREATE DATABASE %I', :db_name);
                END IF;
            END $$;
            """,
        )
        conn.execute(
            sql_query,
            parameters={
                'db_name': db_settings.db_name,
            },
        )
    temp_engine.dispose()


create_database()
Base.metadata.create_all(bind=engine)


class BudgetService:

    @classmethod
    def create_entry(
        cls,
        db: Session,
        entry: BudgetEntrySchema,
    ) -> BudgetEntry:
        db_entry = BudgetEntry(**entry.model_dump(exclude_unset=True))
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry

    @classmethod
    def get_entries(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> list[type[BudgetEntry]]:
        return (
            db.query(BudgetEntry)
            .order_by(BudgetEntry.date.desc())
            .order_by(BudgetEntry.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def update_entries(
        cls,
        db: Session,
        updated_entries: list[BudgetEntrySchema],
    ) -> dict[str, str]:
        updated_entries = sorted(updated_entries, key=lambda entry: entry.id)
        entry_ids = [entry.id for entry in updated_entries]
        entries = (
            db.query(BudgetEntry)
            .filter(BudgetEntry.id.in_(entry_ids))
            .order_by(BudgetEntry.id)
            .all()
        )
        existing_entries = {
            entry.id: entry
            for entry in entries
        }
        for updated_entry in updated_entries:
            # noinspection PyTypeChecker
            entry = existing_entries.get(updated_entry.id, None)
            if entry is None:
                new_entry = BudgetEntry(**updated_entry.model_dump())
                db.add(new_entry)
            else:
                for field, field_value in updated_entry.model_dump().items():
                    setattr(entry, field, field_value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ProcessingError from exc
        return {'message': 'Entries processed successfully.'}

    @classmethod
    def delete_entry(cls, db: Session, entry_id: int) -> dict[str, str]:
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id,
        ).first()
        if entry:
            db.delete(entry)
            db.commit()
            return {'message': 'Entry deleted'}
        raise EntryNotFound
