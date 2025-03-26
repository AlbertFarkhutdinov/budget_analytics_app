import pandas as pd
import sqlalchemy as sql

from backend.entries_app.models import BudgetEntry

ReportType = dict[
    str,
    dict[str, list[float | str]],
]


class ReportsGenerator:

    def __init__(
        self,
        engine: sql.Engine,
    ) -> None:
        self.engine = engine

    def expenses_per_day(self) -> ReportType:
        df = (
            self._fetch_data(query=sql.select(BudgetEntry))
            .groupby('date')
            .sum(numeric_only=True)
            .reset_index()
        )
        return {
            'plot_data': {
                'x': df.index.values.tolist(),
                'y': df['amount'].values.tolist(),
                'columns': ['date', 'amount'],
            },
        }

    def _fetch_data(self, query: sql.Select) -> pd.DataFrame:
        """Fetch data from RDS."""
        with self.engine.connect() as connection:
            return pd.read_sql(query, connection)
