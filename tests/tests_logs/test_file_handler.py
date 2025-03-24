"""Tests for `auxiliary.file_handler` objects."""
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from custom_logging import get_file_handler

log_filepath = Path('.').joinpath('test.log')


class TestFileHandler:
    """Class with tests for `file_handler.get_file_handler`."""

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown any state that was previously setup."""
        if log_filepath.exists():
            os.remove(log_filepath)

    def test_get_file_handler_returns_handler(self) -> None:
        """Test type of returnable handler."""
        logging_handler = get_file_handler(str(log_filepath))
        assert isinstance(logging_handler, logging.Handler)

    def test_get_file_handler_default_logging_level(self) -> None:
        """Test default level of returnable handler."""
        logging_handler = get_file_handler(str(log_filepath))
        assert logging_handler.level == logging.INFO

    def test_get_file_handler_custom_logging_level(self) -> None:
        """Test specified level of returnable handler."""
        logging_handler = get_file_handler(
            filename=str(log_filepath),
            logging_level=logging.DEBUG,
        )
        assert logging_handler.level == logging.DEBUG

    def test_get_file_handler_is_rewritable(self) -> None:
        """Test type and mode of rewritable handler."""
        logging_handler = get_file_handler(
            str(log_filepath),
            is_rewritable=True,
        )
        assert isinstance(logging_handler, logging.FileHandler)
        assert logging_handler.mode == 'w'

    def test_get_file_handler_not_rewritable(self) -> None:
        """Test type of non-rewritable handler."""
        logging_handler = get_file_handler(
            str(log_filepath),
            is_rewritable=False,
        )
        assert isinstance(logging_handler, TimedRotatingFileHandler)

    def test_get_file_handler_formatter(self) -> None:
        """Test format of handler's log messages."""
        logging_handler = get_file_handler(str(log_filepath))
        formatter = logging_handler.formatter
        log_format = json.dumps({
            'loggedAt': '%(asctime)s',
            'level': '%(levelname)s',
            'message': '%(message)s',
            'current_memory': '%(current_memory)sMb',
            'peak_memory': '%(peak_memory)sMb',
            'module': '%(module)s',
            'funcName': '%(funcName)s',
        })
        assert formatter._fmt == log_format  # noqa: WPS437
