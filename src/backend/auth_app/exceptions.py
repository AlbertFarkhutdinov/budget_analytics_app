from http import HTTPStatus

from fastapi import HTTPException


class MissingSecretError(ValueError):
    """Exception raised when secret key for Cognito client is missing."""

    def __init__(self) -> None:
        """Initialize MissingSecretError."""
        super().__init__('COGNITO_CLIENT_SECRET is missing.')


class UserAlreadyExistsError(HTTPException):

    def __init__(self) -> None:
        """Initialize UserAlreadyExistsError."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='User already exists.',
        )


class InvalidConfirmationCodeError(HTTPException):

    def __init__(self) -> None:
        """Initialize InvalidConfirmationCodeError."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid confirmation code.',
        )


class UserNotFoundError(HTTPException):

    def __init__(self) -> None:
        """Initialize UserNotFoundError."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='User not found.',
        )


class IncorrectCredentialsError(HTTPException):

    def __init__(self) -> None:
        """Initialize IncorrectCredentialsError."""
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password.',
        )


class UserNotConfirmedError(HTTPException):

    def __init__(self) -> None:
        """Initialize UserNotConfirmedError."""
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail='User is not confirmed.',
        )


class InternalServerError(HTTPException):

    def __init__(self, detail: str) -> None:
        """Initialize InternalServerError."""
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=detail,
        )
