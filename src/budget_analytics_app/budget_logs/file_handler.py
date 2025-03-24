"""The module contains a function for file handler configuration."""
import json
import logging
import tracemalloc
from logging.handlers import TimedRotatingFileHandler

from budget_analytics_app.budget_logs.record_factory import record_factory


def get_file_handler(
    filename: str,
    logging_level: int = logging.INFO,
    *,
    is_rewritable: bool = False,
) -> logging.Handler:
    """
    Return a handler of file log messages.

    Parameters
    ----------
    filename : str
        The name of the file to which log messages are written.
    logging_level : int, default: logging.INFO
        Minimum message level to be logged into the file.
    is_rewritable : bool, default: False
        Whether log file is rewritable.

    Returns
    -------
    logging.Handler
        A handler of file log messages.

    """
    tracemalloc.start()
    logging.setLogRecordFactory(record_factory)
    log_format = json.dumps({
        'loggedAt': '%(asctime)s',
        'level': '%(levelname)s',
        'message': '%(message)s',
        'current_memory': '%(current_memory)sMb',
        'peak_memory': '%(peak_memory)sMb',
        'module': '%(module)s',
        'funcName': '%(funcName)s',
    })
    if is_rewritable:
        file_handler = logging.FileHandler(filename=filename, mode='w')
    else:
        file_handler = TimedRotatingFileHandler(filename=filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging_level)
    return file_handler
