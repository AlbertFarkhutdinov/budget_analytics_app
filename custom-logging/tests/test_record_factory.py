"""Tests for `auxiliary.record_factory` objects."""
import logging
import tracemalloc
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_logging.record_factory import record_factory

BYTES_IN_MB = 1048576


class TestRecordFactory:
    """Class with tests for `record_factory.record_factory`."""

    @classmethod
    def setup_class(cls) -> None:
        """Set up any state specific to executing the given class."""
        tracemalloc.start()

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown any state that was previously setup."""
        tracemalloc.stop()

    @classmethod
    @pytest.fixture
    def mock_traced_memory(cls) -> Generator[MagicMock | AsyncMock, Any]:
        """
        Fixture to set traced memory values during tests.

        Yields
        ------
        unittest.mock.MagicMock
            Mock for `tracemalloc.get_traced_memory` function.

        """
        with patch('tracemalloc.get_traced_memory') as traced_memory_mock:
            yield traced_memory_mock

    @classmethod
    def test_record_factory_attributes(
        cls,
        mock_traced_memory: MagicMock,
    ) -> None:
        """
        Test LogRecord attributes after setting `record_factory`.

        Parameters
        ----------
        mock_traced_memory : unittest.mock.MagicMock
            Mock for `tracemalloc.get_traced_memory` function.

        """
        logging.setLogRecordFactory(record_factory)
        logger = logging.getLogger('test_logger')

        mock_traced_memory.return_value = (BYTES_IN_MB, 10 * BYTES_IN_MB)
        record = logger.makeRecord(
            name='test_logger',
            level=logging.INFO,
            fn='path',
            lno=10,
            msg='Test message',
            args=(),
            exc_info=None,
        )
        assert getattr(record, 'current_memory', None) == 1
        expected = 10
        assert getattr(record, 'peak_memory', None) == expected

    @classmethod
    def test_record_factory_with_default_log_record(
        cls,
        mock_traced_memory: MagicMock,
    ) -> None:
        """
        Test attributes of LogRecord returned by `record_factory`.

        Parameters
        ----------
        mock_traced_memory : unittest.mock.MagicMock
            Mock for `tracemalloc.get_traced_memory` function.

        """
        default_factory = logging.getLogRecordFactory()
        logging.setLogRecordFactory(default_factory)

        mock_traced_memory.return_value = (BYTES_IN_MB, 10 * BYTES_IN_MB)

        record = record_factory(
            name='test_logger',
            level=logging.INFO,
            pathname='path',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None,
        )
        assert getattr(record, 'current_memory', None) == 1
        expected = 10
        assert getattr(record, 'peak_memory', None) == expected
