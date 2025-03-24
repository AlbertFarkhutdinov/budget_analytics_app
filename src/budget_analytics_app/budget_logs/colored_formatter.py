"""The module contains a class for coloring of log messages."""
import logging


class ColoredFormatter(logging.Formatter):
    """
    Class for coloring of log messages.

    Attributes
    ----------
    colors : dict
        Logging levels and their colors.

    Methods
    -------
    format(record)
        Format the specified record as text.

    """

    colors = {
        logging.DEBUG: '\x1b[38;20m',
        logging.INFO: '\x1b[38;20m',
        logging.WARNING: '\x1b[33;20m',
        logging.ERROR: '\x1b[31;20m',
        logging.CRITICAL: '\x1b[31;1m',
    }

    def __init__(self, format_string: str, *args, **kwargs) -> None:
        """
        Initialize ColoredFormatter instance.

        Parameters
        ----------
        format_string : str
            Format of logged message.
        args : tuple, optional
            Additional arguments: refer to logging.Formatter documentation
            for a list of all possible arguments.
        kwargs : dict, optional
            Additional keyword arguments: refer to logging.Formatter
            documentation for a list of all possible arguments.

        """
        super().__init__(*args, **kwargs)
        self.format_string = format_string

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text.

        Parameters
        ----------
        record : logging.LogRecord
            A log record to be formatted.

        Returns
        -------
        str
            A log record formatted as text.

        """
        color = self.__class__.colors.get(record.levelno)
        formatter = logging.Formatter(
            f'{color}{self.format_string}\x1b[0m',
        )
        return formatter.format(record)
