"""The `custom_logging` library provides custom logging functionality."""
from custom_logging.colored_formatter import ColoredFormatter
from custom_logging.file_handler import get_file_handler
from custom_logging.logging_config import config_logging
from custom_logging.record_factory import record_factory
from custom_logging.stream_handler import get_stream_handler

__all__ = [
    'ColoredFormatter',
    'get_file_handler',
    'config_logging',
    'record_factory',
    'get_stream_handler',
]
