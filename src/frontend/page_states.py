from enum import Enum


class PageState(Enum):
    auth = 'auth'
    entries = 'entries'
    new_entry = 'new_entry'
