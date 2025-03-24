"""The module contains a function for stream handler configuration."""
import logging
import sys

from budget_analytics_app.budget_logs.colored_formatter import ColoredFormatter


def get_stream_handler(
    logging_level: int = logging.DEBUG,
    *,
    verbose: bool = False,
) -> logging.Handler:
    """
    Return handler of file log messages.

    Parameters
    ----------
    logging_level : int, default: logging.DEBUG
        Minimum message level to be logged into stream.
    verbose : bool, default: False.
        Whether is a log message in stream verbose.

    Returns
    -------
    logging.Handler
        A handler of stream log messages.

    """
    msg_items = [
        '%(asctime)s',
        '%(levelname)s',
    ]
    if verbose:
        msg_items.extend(['%(funcName)s', '%(module)s'])
    msg_items.append('%(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(
        ColoredFormatter(' | '.join(msg_items)),
    )
    return stream_handler
