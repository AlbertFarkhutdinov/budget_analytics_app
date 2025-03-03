"""The module contains a configuration of logging."""
import logging

from custom_logging.file_handler import get_file_handler
from custom_logging.stream_handler import get_stream_handler


def config_logging(
    stream_logging_level: int = logging.INFO,
    file_logging_level: int = logging.INFO,
    verbose: bool = False,
    filename: str = '',
    is_rewritable: bool = False,
) -> None:
    """
    Configure logging.

    Parameters
    ----------
    stream_logging_level : int, default: logging.INFO
        Minimum message level to be logged into stream.
    file_logging_level : int, default: logging.INFO
        Minimum message level to be logged into the file.
    verbose : bool, default: False.
        Whether is a log message in stream verbose.
    filename : str, default: ''.
        The name of the file to which log messages are written.
    is_rewritable : bool, default : False
        Whether log file is rewritable.

    """
    handlers = [
        get_stream_handler(
            logging_level=stream_logging_level,
            verbose=verbose,
        ),
    ]
    if filename:
        handlers.append(
            get_file_handler(
                filename=filename,
                is_rewritable=is_rewritable,
                logging_level=file_logging_level,
            ),
        )
    logging.basicConfig(
        level=min(stream_logging_level, file_logging_level),
        handlers=handlers,
    )
