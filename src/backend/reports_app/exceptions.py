"""Custom exception classes for report-related errors."""

from http import HTTPStatus

from fastapi import HTTPException


class ReportNotFound(HTTPException):
    """Exception raised when a report is not found in the storage."""

    def __init__(self) -> None:
        """Initialize ReportNotFound with a default message."""
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='No report found.',
        )


class InvalidReportType(HTTPException):
    """Exception raised when a report type is not supported."""

    def __init__(self) -> None:
        """Initialize ProcessingError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid report type.',
        )
