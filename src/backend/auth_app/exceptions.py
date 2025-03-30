"""
Custom exception classes for authentication-related errors.

This module defines specific exceptions for handling various authentication
errors in an AWS Cognito-based authentication system.

"""

from http import HTTPStatus

from fastapi import HTTPException


class MissingSecretError(ValueError):
    """Exception raised when secret key for Cognito client is missing."""

    def __init__(self) -> None:
        """Initialize MissingSecretError with a default message."""
        super().__init__('COGNITO_CLIENT_SECRET is missing.')


class UserAlreadyExistsError(HTTPException):
    """Exception raised when attempting to register an existing user."""

    def __init__(self) -> None:
        """Initialize UserAlreadyExistsError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='User already exists.',
        )


class InvalidConfirmationCodeError(HTTPException):
    """Exception raised when an invalid confirmation code is provided."""

    def __init__(self) -> None:
        """Initialize InvalidConfirmationCodeError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid confirmation code.',
        )


class UserNotFoundError(HTTPException):
    """Exception raised when a user does not exist in Cognito."""

    def __init__(self) -> None:
        """Initialize UserNotFoundError with a default message."""
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='User not found.',
        )


class IncorrectCredentialsError(HTTPException):
    """Exception raised when login credentials are incorrect."""

    def __init__(self) -> None:
        """Initialize IncorrectCredentialsError with a default message."""
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password.',
        )


class UserNotConfirmedError(HTTPException):
    """Exception raised when a user has not confirmed their account."""

    def __init__(self) -> None:
        """Initialize UserNotConfirmedError with a default message."""
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail='User is not confirmed.',
        )


class InternalServerError(HTTPException):
    """Exception raised for unexpected internal errors."""

    def __init__(self, detail: str) -> None:
        """
        Initialize InternalServerError with a custom error message.

        Parameters
        ----------
        detail : str
            The error message to be included in the response.

        """
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=detail,
        )
