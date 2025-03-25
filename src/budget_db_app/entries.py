from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sql
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from budget_db_app.exceptions import EntryNotFound


class DBSettings(BaseSettings):
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: int = 5432
    db_name: str = ''

    model_config = SettingsConfigDict(
        env_file='src/budget_db_app/.env',
        env_file_encoding='utf-8',
    )


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
    date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    shop = sql.Column(sql.String, index=True)
    product = sql.Column(sql.String)
    amount = sql.Column(sql.Float)
    category = sql.Column(sql.String)
    person = sql.Column(sql.String)
    currency = sql.Column(sql.String)


class BudgetEntrySchema(BaseModel):
    id: Optional[int] = None
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
    def update_entry(
        cls,
        db: Session,
        entry_id: int,
        updated_entry: BudgetEntrySchema,
    ) -> type[BudgetEntry]:
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id,
        ).first()
        if not entry:
            raise EntryNotFound()
        for key, entry_value in updated_entry.model_dump().items():
            setattr(entry, key, entry_value)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def delete_entry(cls, db: Session, entry_id: int) -> dict[str, str]:
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id,
        ).first()
        if entry:
            db.delete(entry)
            db.commit()
            return {'message': 'Entry deleted'}
        raise EntryNotFound()
