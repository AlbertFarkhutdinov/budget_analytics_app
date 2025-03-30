"""The module providing a class for managing budget entries in a database."""
import io

import pandas as pd
import sqlalchemy as sql
from fastapi import UploadFile
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.entries_app.exceptions import MissedColumnsError, NoFileUploaded
from backend.entries_app.models import BudgetEntry, BudgetEntrySchema

MSG_FIELD = 'message'


class BudgetService:
    """Service class for managing budget entries in a database."""

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        """
        Initialize the BudgetService.

        Parameters
        ----------
        engine : sql.Engine
            SQLAlchemy database engine.

        """
        self.engine = engine

    def create_entry(
        self,
        entry: BudgetEntrySchema,
    ) -> dict[str, str]:
        """
        Create a new budget entry.

        Parameters
        ----------
        entry : BudgetEntrySchema
            The budget entry schema containing the entry details.

        Returns
        -------
        dict
            A success message indicating the entry was added.

        """
        with Session(self.engine) as session:
            db_entry = BudgetEntry(**entry.model_dump(exclude_unset=True))
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
            return {MSG_FIELD: 'Entry is added successfully.'}

    def get_entries_info(self) -> dict[str, str | int]:
        """
        Return summary information about the budget entries.

        Returns
        -------
        dict
            A dictionary containing the number of entries, date range,
            number of unique categories, and number of unique persons.

        """
        with Session(self.engine) as session:
            summary = session.query(
                sql.func.count(BudgetEntry.id),
                sql.func.min(BudgetEntry.date),
                sql.func.max(BudgetEntry.date),
                sql.func.count(sql.func.distinct(BudgetEntry.category)),
                sql.func.count(sql.func.distinct(BudgetEntry.person)),
            ).first()
        return {
            'entries_number': summary[0],
            'min_date': summary[1].isoformat() if summary[1] else None,
            'max_date': summary[2].isoformat() if summary[2] else None,
            'categories_number': summary[3],
            'persons_number': summary[4],
        }

    def read_entries(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[BudgetEntry]:
        """
        Return a paginated list of budget entries ordered by date and ID.

        Parameters
        ----------
        skip : int, optional
            Number of entries to skip, by default 0.
        limit : int, optional
            Maximum number of entries to return, by default 10.

        Returns
        -------
        list of BudgetEntry
            A list of budget entries.

        """
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
        """
        Update multiple budget entries.

        Parameters
        ----------
        updated_entries : list of BudgetEntrySchema
            A list of budget entry schemas with updated data.

        Returns
        -------
        dict
            A success message indicating the entries were updated.

        """
        with Session(self.engine) as session:
            for updated_entry in updated_entries:
                self._update_entry(
                    updated_entry=updated_entry,
                    session=session,
                )
            session.commit()
            return {MSG_FIELD: 'Entries are saved successfully.'}

    def upload_entries(
        self,
        uploaded_entries: UploadFile,
    ) -> dict[str, str]:
        """
        Upload and save budget entries from a CSV file.

        Parameters
        ----------
        uploaded_entries : UploadFile
            The uploaded CSV file containing budget entries.

        Returns
        -------
        dict
            A success message indicating the number of uploaded entries.

        """
        if not uploaded_entries:
            raise NoFileUploaded
        df = self._process_upload_entries(uploaded_entries=uploaded_entries)
        with Session(self.engine) as session:
            for record in df.to_dict(orient='records'):
                entry_schema = BudgetEntrySchema(**record)
                db_entry = BudgetEntry(
                    **entry_schema.model_dump(exclude_unset=True),
                )
                session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
            return {
                MSG_FIELD: f'{df.shape[0]} entries is uploaded successfully.',
            }

    def delete_all_entries(self) -> dict[str, str]:
        """
        Delete all budget entries from the database.

        Returns
        -------
        dict
            A success message indicating all entries were deleted.

        """
        with Session(self.engine) as session:
            session.query(BudgetEntry).delete()
            session.commit()
            return {MSG_FIELD: 'All entries are deleted successfully.'}

    @classmethod
    def _update_entry(
        cls,
        updated_entry: BudgetEntrySchema,
        session: Session,
    ) -> None:
        """
        Update or insert a single budget entry.

        Parameters
        ----------
        updated_entry : BudgetEntrySchema
            The budget entry schema with updated data.
        session : Session
            The database session.

        """
        stmt = (
            sql.select(BudgetEntry)
            .where(BudgetEntry.id.in_([updated_entry.id]))
            .order_by(BudgetEntry.id)
        )
        try:
            entry = session.scalars(stmt).one()
        except NoResultFound:
            dumped_model = updated_entry.model_dump(exclude_unset=True)
            if dumped_model.get('id') in {-1, None}:
                dumped_model.pop('id')
            entry = BudgetEntry(**dumped_model)
            session.add(entry)
        else:
            for entry_field in updated_entry.model_dump().items():
                setattr(entry, *entry_field)

    @classmethod
    def _process_upload_entries(
        cls,
        uploaded_entries: UploadFile,
    ) -> pd.DataFrame:
        """
        Process and validate uploaded CSV entries.

        Parameters
        ----------
        uploaded_entries : UploadFile
            The uploaded CSV file.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the validated budget entries.

        Raises
        ------
        MissedColumnsError
            If required columns are missing from the uploaded file.

        """
        df = pd.read_csv(
            io.StringIO(uploaded_entries.file.read().decode('utf-8')),
            sep=';',
        )
        expected_fields = {**BudgetEntrySchema.model_fields}
        expected_fields.pop('id')
        missed_columns = [
            column
            for column in expected_fields
            if column not in df.columns
        ]
        if missed_columns:
            raise MissedColumnsError(missed_columns=missed_columns)

        df['date'] = pd.to_datetime(df['date'])
        return df
