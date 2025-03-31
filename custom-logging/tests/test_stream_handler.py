"""Tests for `auxiliary.stream_handler` objects."""
import logging

import custom_logging as logs


class TestStreamHandler:
    """Class with tests for `stream_handler.get_stream_handler`."""

    @classmethod
    def test_get_file_handler_returns_handler(cls) -> None:
        """Test type of returnable handler."""
        logging_handler = logs.get_stream_handler()
        assert isinstance(logging_handler, logging.Handler)

    @classmethod
    def test_get_file_handler_default_logging_level(cls) -> None:
        """Test default level of returnable handler."""
        logging_handler = logs.get_stream_handler()
        assert logging_handler.level == logging.DEBUG

    @classmethod
    def test_get_file_handler_custom_logging_level(cls) -> None:
        """Test specified level of returnable handler."""
        logging_handler = logs.get_stream_handler(
            logging_level=logging.WARNING,
        )
        assert logging_handler.level == logging.WARNING

    @classmethod
    def test_get_file_handler_verbose(cls) -> None:
        """Test type and mode of verbose handler."""
        logging_handler = logs.get_stream_handler(verbose=True)
        formatter = logging_handler.formatter
        expected_format = ' | '.join([  # noqa: FLY002
            '%(asctime)s',
            '%(levelname)s',
            '%(funcName)s',
            '%(module)s',
            '%(message)s',
        ])
        if isinstance(formatter, logs.ColoredFormatter):
            assert formatter.format_string == expected_format

    @classmethod
    def test_get_file_handler_not_verbose(cls) -> None:
        """Test type of non-verbose handler."""
        logging_handler = logs.get_stream_handler(verbose=False)
        formatter = logging_handler.formatter
        expected_format = '%(asctime)s | %(levelname)s | %(message)s'
        if isinstance(formatter, logs.ColoredFormatter):
            assert formatter.format_string == expected_format
