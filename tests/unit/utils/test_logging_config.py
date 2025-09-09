"""Unit tests for logging configuration system."""

import logging
import sys
from pathlib import Path

from src.utils.logging_config import (
    ColoredFormatter,
    get_logger,
    setup_logging,
)


class TestColoredFormatter:
    """Test cases for ColoredFormatter class."""

    def test_color_application_for_all_levels(self):
        """Test ANSI color codes are correctly applied to each log level."""
        formatter = ColoredFormatter("%(levelname)s %(message)s")

        test_cases = [
            ("DEBUG", "\033[36m"),  # Cyan
            ("INFO", "\033[32m"),  # Green
            ("WARNING", "\033[33m"),  # Yellow
            ("ERROR", "\033[31m"),  # Red
            ("CRITICAL", "\033[35m"),  # Magenta
        ]

        for level_name, expected_color in test_cases:
            record = logging.LogRecord(
                name="test",
                level=getattr(logging, level_name),
                pathname="",
                lineno=0,
                msg="test message",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)
            assert expected_color in formatted
            assert "\033[0m" in formatted  # Reset code

    def test_levelname_preservation(self):
        """Test original levelname is restored after formatting."""
        formatter = ColoredFormatter("%(levelname)s %(message)s")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        original_levelname = record.levelname
        formatter.format(record)

        # Levelname should be restored to original value
        assert record.levelname == original_levelname

    def test_unknown_level_handling(self):
        """Test behavior with custom/unknown log levels not in COLORS dict."""
        formatter = ColoredFormatter("%(levelname)s %(message)s")

        # Create record with custom level not in COLORS
        record = logging.LogRecord(
            name="test",
            level=25,  # Custom level between INFO(20) and WARNING(30)
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        formatted = formatter.format(record)

        # Should not crash and should not contain color codes for unknown level
        assert "CUSTOM" in formatted
        # Should not contain any ANSI color codes since CUSTOM not in COLORS
        assert "\033[" not in formatted or formatted.count("\033[") == 0


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_default_behavior(self):
        """Test console handler with INFO level, no file logging."""
        logger = setup_logging()

        assert logger.name == "fluent_forever"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1

        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream is sys.stdout
        assert isinstance(handler.formatter, ColoredFormatter)

    def test_handler_deduplication(self):
        """Test multiple calls don't create duplicate handlers."""
        # First call
        logger1 = setup_logging(level=logging.DEBUG)
        initial_handler_count = len(logger1.handlers)

        # Second call on same logger
        logger2 = setup_logging(level=logging.INFO)

        # Should be same logger instance with same number of handlers
        assert logger1 is logger2
        assert len(logger2.handlers) == initial_handler_count

    def test_file_logging_activation(self, tmp_path):
        """Test file handler created when log_to_file=True."""
        log_file = tmp_path / "test.log"

        logger = setup_logging(log_to_file=True, log_file_path=log_file)

        assert len(logger.handlers) == 2  # Console + File

        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert Path(file_handler.baseFilename) == log_file

    def test_directory_creation(self, tmp_path):
        """Test log directory created when it doesn't exist."""
        log_dir = tmp_path / "logs" / "nested"
        log_file = log_dir / "test.log"

        assert not log_dir.exists()

        setup_logging(log_to_file=True, log_file_path=log_file)

        assert log_dir.exists()
        assert log_file.exists()

    def test_level_propagation(self, tmp_path):
        """Test specified log level applies to both console and file handlers."""
        log_file = tmp_path / "test.log"
        test_level = logging.WARNING

        logger = setup_logging(
            level=test_level, log_to_file=True, log_file_path=log_file
        )

        assert logger.level == test_level

        for handler in logger.handlers:
            assert handler.level == test_level

    def test_file_creation_failure_handling(self, tmp_path):
        """Test behavior when log file path is invalid/unwritable."""
        # Try to create log file in non-existent directory without parent creation
        invalid_path = tmp_path / "nonexistent" / "deeply" / "nested" / "test.log"

        # Should not raise exception during setup_logging call
        # The mkdir(exist_ok=True) should create the parent directories
        logger = setup_logging(log_to_file=True, log_file_path=invalid_path)

        # Should still have console handler even if file logging fails
        console_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.FileHandler)
        ]
        assert len(console_handlers) >= 1


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_module_name_formatting(self):
        """Test logger name correctly formatted as fluent_forever.{module_name}."""
        module_name = "anki.connection"
        logger = get_logger(module_name)

        assert logger.name == f"fluent_forever.{module_name}"

        # Test with different module names
        test_cases = [
            "core.config",
            "providers.openai",
            "stages.validation",
            "cli.commands",
        ]

        for module in test_cases:
            logger = get_logger(module)
            assert logger.name == f"fluent_forever.{module}"
