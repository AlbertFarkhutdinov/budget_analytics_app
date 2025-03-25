from http import HTTPStatus

from fastapi import HTTPException


class EntryNotFound(HTTPException):

    def __init__(self) -> None:
        """Initialize EntryNotFound."""
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Entry not found.',
        )
