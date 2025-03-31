"""The module contains an object which is used to create a log record."""
import logging
import tracemalloc

OLD_FACTORY = logging.getLogRecordFactory()


def record_factory(*args, **kwargs) -> logging.LogRecord:
    """
    Return an object which is used to create a log record.

    Parameters
    ----------
    args : optional
        Arguments of standard Log Record Factory.
    kwargs : optional
        Keyword arguments of standard Log Record Factory.

    Returns
    -------
    logging.LogRecord
        An object which is used to create a log record.

    """
    record = OLD_FACTORY(*args, **kwargs)
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    record.current_memory = round(current_memory / 1024 / 1024, 2)
    record.peak_memory = round(peak_memory / 1024 / 1024, 2)
    return record
