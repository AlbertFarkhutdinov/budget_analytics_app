from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sql
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from budget_analytics_app.budget_logs import config_logging


class DBSettings(BaseSettings):
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: int = 5432
    db_name: str = ''

    model_config = SettingsConfigDict(
        env_file='env/db',
        env_file_encoding='utf-8',
    )


config_logging()
db_settings = DBSettings()


DATABASE_URL = URL.create(
    drivername='postgresql',
    username=db_settings.db_user,
    password=db_settings.db_password,
    host=db_settings.db_host,
    port=db_settings.db_port,
    database=db_settings.db_name,
)


class Database:
    engine = sql.create_engine(
        URL.create(
            drivername='postgresql',
            username=db_settings.db_user,
            password=db_settings.db_password,
            host=db_settings.db_host,
            port=db_settings.db_port,
            database=db_settings.db_name,
        ),
    )
    session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    base = declarative_base()

    @classmethod
    def create_database(cls) -> None:
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
            db_name = db_settings.db_name
            query_result = conn.execute(
                sql.text(
                    f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
                ),
            )
            if not query_result.fetchone():
                conn.execute(
                    sql.text(f'CREATE DATABASE {db_settings.db_name}'),
                )
        temp_engine.dispose()


Database.create_database()
Database.base.metadata.create_all(bind=Database.engine)


class BudgetEntry(Database.base):
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


class BudgetService:

    @classmethod
    def create_entry(
        cls,
        db: Session,
        entry: BudgetEntrySchema,
    ) -> BudgetEntry:
        db_entry = BudgetEntry(**entry.model_dump())
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
        return db.query(BudgetEntry).offset(skip).limit(limit).all()

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
            raise HTTPException(status_code=404, detail='Entry not found')
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


def get_db() -> Database.session_local:
    db = Database.session_local()
    try:
        yield db
    finally:
        db.close()


entries_router = APIRouter()


@entries_router.get(path='/', response_model=list[BudgetEntrySchema])
def read_entries(
    db: Session = Depends(get_db),
) -> list[type[BudgetEntry]]:
    return BudgetService.get_entries(db)


@entries_router.post(path='/')
def create_entry(
    entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
) -> BudgetEntry:
    return BudgetService.create_entry(db, entry)


@entries_router.put(path='/{entry_id}', response_model=BudgetEntrySchema)
def update_entry(
    entry_id: int,
    updated_entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
) -> type[BudgetEntry]:
    return BudgetService.update_entry(db, entry_id, updated_entry)


@entries_router.delete(path='/{entry_id}')
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    return BudgetService.delete_entry(db, entry_id)
