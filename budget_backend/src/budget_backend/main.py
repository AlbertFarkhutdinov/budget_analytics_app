import logging
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sql
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class DBSettings(BaseSettings):
    DB_USER: str = ''
    DB_PASSWORD: str = ''
    DB_HOST: str = ''
    DB_PORT: int = 5432
    DB_NAME: str = ''

    model_config = SettingsConfigDict(
        env_file='env/db',
        env_file_encoding='utf-8',
    )


db_settings = DBSettings()


DATABASE_URL = URL.create(
    drivername='postgresql',
    username=db_settings.DB_USER,
    password=db_settings.DB_PASSWORD,
    host=db_settings.DB_HOST,
    port=db_settings.DB_PORT,
    database=db_settings.DB_NAME
)


class Database:
    engine = sql.create_engine(
        URL.create(
            drivername='postgresql',
            username=db_settings.DB_USER,
            password=db_settings.DB_PASSWORD,
            host=db_settings.DB_HOST,
            port=db_settings.DB_PORT,
            database=db_settings.DB_NAME
        )
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base = declarative_base()

    @staticmethod
    def create_database():
        temp_engine = sql.create_engine(
            URL.create(
                drivername='postgresql',
                username=db_settings.DB_USER,
                password=db_settings.DB_PASSWORD,
                host=db_settings.DB_HOST,
                port=db_settings.DB_PORT,
                database='postgres',
            )
        )
        with temp_engine.connect() as conn:
            conn.execute(sql.text('COMMIT'))
            result = conn.execute(
                sql.text(
                    "SELECT 1 FROM pg_database WHERE datname='{0}'".format(
                        db_settings.DB_NAME
                    )
                )
            )
            if not result.fetchone():
                conn.execute(
                    sql.text(f'CREATE DATABASE {db_settings.DB_NAME}')
                )
        temp_engine.dispose()


Database.create_database()
Database.Base.metadata.create_all(bind=Database.engine)


class BudgetEntry(Database.Base):
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

    @staticmethod
    def create_entry(db: Session, entry: BudgetEntrySchema) -> BudgetEntry:
        db_entry = BudgetEntry(**entry.model_dump())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry

    @staticmethod
    def get_entries(
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> list[BudgetEntry]:
        return db.query(BudgetEntry).offset(skip).limit(limit).all()

    @staticmethod
    def update_entry(
        db: Session,
        entry_id: int,
        updated_entry: BudgetEntrySchema,
    ) -> BudgetEntry:
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail='Entry not found')
        for key, value in updated_entry.model_dump().items():
            setattr(entry, key, value)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete_entry(db: Session, entry_id: int):
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
        return {'message': 'Entry deleted'}


app = FastAPI()


def get_db():
    db = Database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(path='/entries/', response_model=list[BudgetEntrySchema])
def read_entries(
    db: Session = Depends(get_db),
):
    return BudgetService.get_entries(db)


@app.post(path='/entries/')
def create_entry(
    entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
):
    return BudgetService.create_entry(db, entry)


@app.put(path='/entries/{entry_id}', response_model=BudgetEntrySchema)
def update_entry(
    entry_id: int,
    updated_entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
):
    return BudgetService.update_entry(db, entry_id, updated_entry)


@app.delete(path='/entries/{entry_id}')
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    return BudgetService.delete_entry(db, entry_id)
