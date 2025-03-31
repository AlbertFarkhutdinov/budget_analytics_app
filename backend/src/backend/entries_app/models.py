"""The module providing Pydantic models for database-related requests."""
from datetime import UTC, datetime

import sqlalchemy as sql
from pydantic import BaseModel
from sqlalchemy import orm


class Base(orm.DeclarativeBase):
    """Base class for SQLAlchemy models."""


class BudgetEntry(Base):
    """
    SQLAlchemy model representing a budget entry.

    Attributes
    ----------
    id : int
        Unique identifier for the budget entry.
    date : datetime
        Timestamp of the budget entry (default: current UTC time).
    shop : str
        Name of the shop where the purchase was made.
    product : str
        Name of the purchased product.
    amount : float
        Amount spent on the product.
    category : str
        Category of the expense.
    person : str
        Name of the person making the purchase.
    currency : str
        Currency used for the transaction.

    """

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
    """
    Pydantic schema for budget entry validation.

    Attributes
    ----------
    id : int, optional
        Unique identifier for the budget entry.
    date : datetime
        Timestamp of the budget entry.
    shop : str
        Name of the shop where the purchase was made.
    product : str
        Name of the purchased product.
    amount : float
        Amount spent on the product.
    category : str
        Category of the expense.
    person : str
        Name of the person making the purchase.
    currency : str
        Currency used for the transaction.

    """

    id: int | None = None
    date: datetime
    shop: str
    product: str
    amount: float
    category: str
    person: str
    currency: str

    class Config:
        """
        Configuration for the Pydantic model.

        Attributes
        ----------
        from_attributes : bool, optional
            Enables model initialization from ORM objects.

        """

        from_attributes = True
