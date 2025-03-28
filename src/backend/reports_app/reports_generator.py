import pandas as pd
import sqlalchemy as sql

from backend.entries_app.models import BudgetEntry

ReportType = dict[
    str,
    dict[str, list[float | str]],
]
ReportsType = dict[str, ReportType]


class ReportsGenerator:

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        self.engine = engine

    def expenses_per_category(self) -> ReportsType:
        grouped_df = self._fetch_data(query=sql.select(BudgetEntry))
        reports = {}
        for interval_name in ('month', 'year'):
            reports[interval_name] = {
                str(interval): (
                    group
                    .groupby('category')
                    .sum(numeric_only=True)['amount']
                    .round(2)
                    .reset_index()
                    .to_dict('list')
                )
                for interval, group in grouped_df.groupby(interval_name)
            }
        reports['total'] = {
            'total': (
                grouped_df
                .groupby('category')
                .sum(numeric_only=True)['amount']
                .round(2)
                .reset_index()
                .to_dict('list')
            ),
        }
        return reports

    def expenses_per_interval(self) -> ReportsType:
        grouped_df = self._fetch_data(query=sql.select(BudgetEntry))
        reports = {}
        for category, group in grouped_df.groupby('category'):
            report = {}
            for interval_name in ('month', 'year'):
                report[interval_name] = (
                    group
                    .groupby(interval_name)
                    .sum(numeric_only=True)['amount']
                    .round(2)
                    .reset_index()
                    .to_dict('list')
                )
            report['total'] = {
                'total': ['total'],
                'amount': [float(group['amount'].sum().round(2))],
            }
            reports[str(category)] = report
        return reports

    def _fetch_data(self, query: sql.Select) -> pd.DataFrame:
        """Fetch data from RDS."""
        with self.engine.connect() as connection:
            return (
                pd.read_sql(query, connection)
                .query('amount > 0')
                .assign(
                    year=lambda df: df['date'].dt.year.astype(str),
                    month=lambda df: df['date'].dt.strftime('%Y-%m'),
                )
                .groupby(['year', 'month', 'date', 'category'])
                .sum(numeric_only=True)
                .reset_index()
            )
