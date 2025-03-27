import io

import pandas as pd
import sqlalchemy as sql
from fastapi import UploadFile
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.entries_app.exceptions import NoFileUploaded, MissedColumnsError
from backend.entries_app.models import BudgetEntry, BudgetEntrySchema


class BudgetService:

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        self.engine = engine

    def create_entry(
        self,
        entry: BudgetEntrySchema,
    ) -> dict[str, str]:
        with Session(self.engine) as session:
            db_entry = BudgetEntry(**entry.model_dump(exclude_unset=True))
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
            return {'message': 'Entries processed successfully.'}

    def read_entries(
        self,
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
        with Session(self.engine) as session:
            return list(session.scalars(stmt))

    def update_entries(
        self,
        updated_entries: list[BudgetEntrySchema],
    ) -> dict[str, str]:
        with Session(self.engine) as session:
            for updated_entry in updated_entries:
                stmt = (
                    sql.select(BudgetEntry)
                    .where(BudgetEntry.id.in_([updated_entry.id]))
                    .order_by(BudgetEntry.id)
                )
                try:
                    entry = session.scalars(stmt).one()
                except NoResultFound:
                    dumped_model = updated_entry.model_dump(exclude_unset=True)
                    entry_id = dumped_model.get('id')
                    if entry_id in {-1, None}:
                        dumped_model.pop('id')
                    entry = BudgetEntry(**dumped_model)
                    session.add(entry)
                else:
                    for key, field in updated_entry.model_dump().items():
                        setattr(entry, key, field)
            session.commit()
            return {'message': 'Entries processed successfully.'}

    def upload_entries(
        self,
        uploaded_entries: UploadFile,
    ) -> dict[str, str]:
        if not uploaded_entries:
            raise NoFileUploaded
        contents = uploaded_entries.file.read()
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')),
            sep=';',
        )
        expected_columns = (
            'date',
            'shop',
            'product',
            'amount',
            'category',
            'person',
            'currency',
        )
        missed_columns = []
        for column in expected_columns:
            if column not in df.columns:
                missed_columns.append(column)
        if missed_columns:
            raise MissedColumnsError(missed_columns=missed_columns)

        return {'message': 'Entries uploaded successfully.'}
