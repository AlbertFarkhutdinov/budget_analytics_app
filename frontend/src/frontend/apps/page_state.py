"""The module defines an enumeration for various page states in the app."""
from enum import Enum


class PageState(Enum):
    """
    An enumeration class that represents various page states in the app.

    Attributes
    ----------
    auth : str
        The authentication page.
    entries : str
        The entries page.
    reports : str
        The reports page.

    """

    auth = 'auth'
    entries = 'entries'
    reports = 'reports'
