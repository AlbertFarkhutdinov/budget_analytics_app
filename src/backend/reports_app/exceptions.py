from http import HTTPStatus

from fastapi import HTTPException


class ReportNotFound(HTTPException):

    def __init__(self) -> None:
        """Initialize ReportNotFound."""
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='No report found.',
        )


class InvalidReportType(HTTPException):

    def __init__(self) -> None:
        """Initialize ProcessingError."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid report type.',
        )
