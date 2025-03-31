"""Tests for `auxiliary.logging_config` objects."""
import logging
from pathlib import Path

from custom_logging import ColoredFormatter, config_logging

log_filepath = Path().joinpath('test.log')


class TestConfigLogging:
    """Tests for `config_logging` without FileHandler."""

    @classmethod
    def test_default_config(cls) -> None:
        """Test `config_logging` with default parameters."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging()
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert root_logger.handlers[0].level == logging.INFO

    @classmethod
    def test_custom_stream_logging_level(cls) -> None:
        """Test `config_logging` with specified stream_logging_level."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(stream_logging_level=logging.DEBUG)
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert root_logger.handlers[0].level == logging.DEBUG

    @classmethod
    def test_not_verbose(cls) -> None:
        """Test `config_logging` with not verbose StreamHandler."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(verbose=False)

        stream_handler = next(
            logging_handler
            for logging_handler in root_logger.handlers
            if isinstance(logging_handler, logging.StreamHandler)
        )
        if isinstance(stream_handler.formatter, ColoredFormatter):
            expected_format = '%(asctime)s | %(levelname)s | %(message)s'
            assert stream_handler.formatter.format_string == expected_format

    @classmethod
    def test_verbose(cls) -> None:
        """Test `config_logging` with verbose StreamHandler."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(verbose=True)
        stream_handler = next(
            logging_handler
            for logging_handler in root_logger.handlers
            if isinstance(logging_handler, logging.StreamHandler)
        )
        if isinstance(stream_handler.formatter, ColoredFormatter):
            expected_format = ' | '.join([  # noqa: FLY002
                '%(asctime)s',
                '%(levelname)s',
                '%(funcName)s',
                '%(module)s',
                '%(message)s',
            ])
            assert stream_handler.formatter.format_string == expected_format


class TestConfigLoggingWithFile:
    """Tests for `config_logging` with FileHandler."""

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown any state that was previously setup."""
        if log_filepath.exists():
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            log_filepath.unlink(missing_ok=True)

    @classmethod
    def test_custom_file_logging_level(cls) -> None:
        """Test `config_logging` with specified file_logging_level."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(
            filename=str(log_filepath),
            file_logging_level=logging.ERROR,
        )
        root_logger = logging.getLogger()
        expected = 2
        assert len(root_logger.handlers) == expected
        file_handler = next(
            logging_handler
            for logging_handler in root_logger.handlers
            if isinstance(logging_handler, logging.FileHandler)
        )
        assert file_handler.level == logging.ERROR

    @classmethod
    def test_rewritable_file_handler(cls) -> None:
        """Test `config_logging` with rewritable FileHandler."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(
            filename=str(log_filepath),
            is_rewritable=True,
        )
        file_handler = next(
            logging_handler
            for logging_handler in root_logger.handlers
            if isinstance(logging_handler, logging.FileHandler)
        )
        assert file_handler.mode == 'w'

    @classmethod
    def test_combined_handlers(cls) -> None:
        """Test `config_logging` with different logging levels."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        config_logging(
            stream_logging_level=logging.WARNING,
            file_logging_level=logging.ERROR,
            filename=str(log_filepath),
        )
        expected = 2
        assert len(root_logger.handlers) == expected

        valid_handlers = 0
        for logging_handler in root_logger.handlers:
            is_stream = isinstance(logging_handler, logging.StreamHandler)
            if is_stream and logging_handler.level == logging.WARNING:
                valid_handlers += 1
            if not is_stream and logging_handler.level == logging.ERROR:
                valid_handlers += 1
        assert valid_handlers
