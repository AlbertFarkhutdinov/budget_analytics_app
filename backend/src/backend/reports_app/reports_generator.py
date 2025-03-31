"""Module for generating financial reports from a database."""
from enum import Enum

import pandas as pd
import sqlalchemy as sql

from backend.entries_app.models import BudgetEntry

ReportType = dict[
    str,
    dict[str, list[float | str]],
]
ReportsType = dict[str, ReportType]


class TimeInterval(Enum):
    """Enumeration for different time intervals used in reports."""

    month: str = 'month'
    year: str = 'year'
    total: str = 'total'


class Column(Enum):
    """Enumeration for column names used in financial data."""

    year: str = 'year'
    month: str = 'month'
    date: str = 'date'
    category: str = 'category'
    amount: str = 'amount'


class ReportsGenerator:
    """Class for generating financial reports based on budget entries."""

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        """
        Initialize ReportsGenerator.

        Parameters
        ----------
        engine : sql.Engine
            SQLAlchemy database engine for executing queries.

        """
        self.engine = engine

    def expenses_per_category(self) -> ReportsType:
        """
        Generate expense reports categorized by time intervals.

        Returns
        -------
        ReportsType
            A dictionary containing total and interval-based expenses
            per category.

        """
        grouped_df = self._fetch_data(query=sql.select(BudgetEntry))
        reports = {}
        for field in TimeInterval:
            if field == TimeInterval.total:
                reports[field.value] = {
                    field.value: (
                        grouped_df
                        .groupby(Column.category.value)
                        .sum(numeric_only=True)[Column.amount.value]
                        .round(2)
                        .reset_index()
                        .to_dict('list')
                    ),
                }
            else:
                reports[field.value] = {
                    str(interval): (
                        group
                        .groupby(Column.category.value)
                        .sum(numeric_only=True)[Column.amount.value]
                        .round(2)
                        .reset_index()
                        .to_dict('list')
                    )
                    for interval, group in grouped_df.groupby(field.value)
                }
        return reports

    def expenses_per_interval(self) -> ReportsType:
        """
        Generate expense reports grouped by category and time intervals.

        Returns
        -------
        ReportsType
            A dictionary containing total and interval-based expenses
            per category.

        """
        grouped_df = self._fetch_data(query=sql.select(BudgetEntry))
        reports = {}
        for category, group in grouped_df.groupby(Column.category.value):
            reports[str(category)] = {}
            for field in TimeInterval:
                if field == TimeInterval.total:
                    reports[str(category)][field.value] = {
                        field.value: [field.value],
                        Column.amount.value: [
                            float(group[Column.amount.value].sum().round(2)),
                        ],
                    }
                else:
                    reports[str(category)][field.value] = (
                        group
                        .groupby(field.value)
                        .sum(numeric_only=True)[Column.amount.value]
                        .round(2)
                        .reset_index()
                        .to_dict('list')
                    )
        return reports

    def _fetch_data(self, query: sql.Select) -> pd.DataFrame:
        """
        Fetch financial data from the database.

        Parameters
        ----------
        query : sql.Select
            SQLAlchemy query to fetch budget entries.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing processed financial data
            with time-based aggregations.

        """
        with self.engine.connect() as connection:
            amount_column = Column.amount.value
            expenses = (
                pd.read_sql(query, connection)
                .query(f'{amount_column} > 0')
            )
            columns = [col.name for col in Column if col.name != 'amount']
            return (
                expenses
                .assign(
                    year=expenses[Column.date.value].dt.year.astype(str),
                    month=expenses[Column.date.value].dt.strftime('%Y-%m'),
                )
                .groupby(columns)
                .sum(numeric_only=True)
                .reset_index()
            )
