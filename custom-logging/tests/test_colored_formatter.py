"""Tests for `auxiliary.colored_formatter` objects."""
import logging

import pytest

from custom_logging import ColoredFormatter


class TestColoredFormatter:
    """Class with tests for `colored_formatter.ColoredFormatter`."""

    @pytest.mark.parametrize(('msg', 'logging_level', 'expected'), [
        (
            'Debug message',
            logging.DEBUG,
            '\x1b[38;20mDEBUG: Debug message\x1b[0m',
        ),
        (
            'Info message',
            logging.INFO,
            '\x1b[38;20mINFO: Info message\x1b[0m',
        ),
        (
            'Warning message',
            logging.WARNING,
            '\x1b[33;20mWARNING: Warning message\x1b[0m',
        ),
        (
            'Error message',
            logging.ERROR,
            '\x1b[31;20mERROR: Error message\x1b[0m',
        ),
        (
            'Critical message',
            logging.CRITICAL,
            '\x1b[31;1mCRITICAL: Critical message\x1b[0m',
        ),
    ])
    def test_format(
        self,
        msg: str,
        logging_level: int,
        expected: str,
    ) -> None:
        """
        Test `colored_formatter.ColoredFormatter.format`.

        Parameters
        ----------
        msg : str
            A log message to be formatted.
        logging_level : int
            A logging level.
        expected : str
            A formatted log message.

        """
        log_record = logging.LogRecord(
            name='test_logger',
            level=logging_level,
            pathname=__file__,
            lineno=10,
            msg=msg,
            args=None,
            exc_info=None,
        )
        formatted_message = ColoredFormatter(
            '%(levelname)s: %(message)s',
        ).format(log_record)
        assert formatted_message == expected
