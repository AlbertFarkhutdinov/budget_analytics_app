from http import HTTPStatus

from fastapi import HTTPException


class EntryNotFound(HTTPException):

    def __init__(self) -> None:
        """Initialize EntryNotFound."""
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Entry not found.',
        )


class ProcessingError(HTTPException):

    def __init__(self) -> None:
        """Initialize ProcessingError."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Error processing entries.',
        )


class NoFileUploaded(HTTPException):

    def __init__(self) -> None:
        """Initialize NoFileUploaded."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No file uploaded.',
        )
