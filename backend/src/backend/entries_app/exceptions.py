"""Custom exception classes for database-related errors."""

from http import HTTPStatus

from fastapi import HTTPException


class EntryNotFound(HTTPException):
    """Exception raised when an entry is not found."""

    def __init__(self) -> None:
        """Initialize EntryNotFound with a default message."""
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Entry not found.',
        )


class ProcessingError(HTTPException):
    """Exception raised when entries are not processed."""

    def __init__(self) -> None:
        """Initialize ProcessingError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Error processing entries.',
        )


class NoFileUploaded(HTTPException):
    """Exception raised when no file is uploaded."""

    def __init__(self) -> None:
        """Initialize NoFileUploaded with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No file uploaded.',
        )


class MissedColumnsError(HTTPException):
    """Exception raised when there are missed columns in a CSV file."""

    def __init__(self, missed_columns: list[str]) -> None:
        """Initialize MissedColumnsError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Missed columns in CSV file: {missed_columns}',
        )
