"""The module providing Pydantic models for user-related requests."""
from pydantic import BaseModel


class UserLogin(BaseModel):
    """
    Pydantic model for user login request.

    Attributes
    ----------
    username : str
        The username of the user attempting to log in.
    password : str
        The password of the user attempting to log in.

    """

    username: str
    password: str


class UserConfirm(BaseModel):
    """
    Pydantic model for user confirmation request.

    Attributes
    ----------
    username : str
        The username of the user confirming their account.
    confirmation_code : str, optional
        The confirmation code sent to the user. Defaults to an empty string.

    """

    username: str
    confirmation_code: str = ''
