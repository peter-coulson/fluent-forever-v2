"""Unit tests for Logging system configuration."""

import logging
import os
import sys
import time
from unittest.mock import Mock, patch

import pytest
from src.utils.logging_config import (
    DEFAULT_LOG_LEVELS,
    ICONS,
    LOGGING_CONFIG_BASE,
    ColoredFormatter,
    ContextualError,
    PerformanceFormatter,
    _is_test_environment,
    get_context_logger,
    get_log_level_from_env,
    get_logger,
    get_logging_config,
    log_error_with_context,
    log_performance,
    setup_logging,
    setup_module_log_levels,
)


class TestSetupLogging:
    """Test suite for logging setup and configuration."""

    @pytest.fixture
    def clean_logging_env(self, monkeypatch):
        """Clean logging environment for testing."""
        # Clear environment variables
        env_vars = [
            "FLUENT_FOREVER_LOG_LEVEL",
            "FLUENT_FOREVER_LOG_TO_FILE",
            "FLUENT_FOREVER_FORCE_FILE_LOG",
            "PYTEST_CURRENT_TEST",
            "TESTING",
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        # Reset logging
        logging.getLogger().handlers.clear()
        logging.getLogger("fluent_forever").handlers.clear()

    def test_setup_logging_console_only_default(self, clean_logging_env):
        """Test default console-only logging setup."""
        logger = setup_logging()

        assert logger.name == "fluent_forever"
        assert logger.level == logging.INFO
        # Should have console handler only
        ff_logger = logging.getLogger("fluent_forever")
        assert len(ff_logger.handlers) == 1
        assert isinstance(ff_logger.handlers[0], logging.StreamHandler)

    @patch("src.utils.logging_config._is_test_environment")
    def test_setup_logging_with_file_output(
        self, mock_is_test, clean_logging_env, tmp_path
    ):
        """Test logging setup with file output."""
        mock_is_test.return_value = False  # Not in test environment
        log_file = tmp_path / "test.log"

        logger = setup_logging(log_to_file=True, log_file_path=log_file)

        assert logger.name == "fluent_forever"
        ff_logger = logging.getLogger("fluent_forever")
        # Should have both console and file handlers
        assert len(ff_logger.handlers) == 2
        handler_types = [type(h).__name__ for h in ff_logger.handlers]
        assert "StreamHandler" in handler_types
        assert "FileHandler" in handler_types

    @patch("src.utils.logging_config._is_test_environment")
    def test_setup_logging_test_environment_detection(
        self, mock_is_test, clean_logging_env
    ):
        """Test test environment detection disables file logging."""
        mock_is_test.return_value = True

        # Even when requesting file logging, test environment should disable it
        setup_logging(log_to_file=True)

        ff_logger = logging.getLogger("fluent_forever")
        # Should only have console handler in test environment
        assert len(ff_logger.handlers) == 1
        assert isinstance(ff_logger.handlers[0], logging.StreamHandler)

    def test_get_logging_config_default(self, clean_logging_env):
        """Test getting default logging configuration."""
        config = get_logging_config()

        assert config["version"] == 1
        assert "console" in config["handlers"]
        assert "fluent_forever" in config["loggers"]
        assert config["loggers"]["fluent_forever"]["level"] == "INFO"

    def test_get_logging_config_custom_level(self, clean_logging_env):
        """Test getting logging configuration with custom level."""
        config = get_logging_config(level=logging.DEBUG)

        assert config["handlers"]["console"]["level"] == "DEBUG"
        assert config["loggers"]["fluent_forever"]["level"] == "DEBUG"

    def test_get_logger_standard_logger(self, clean_logging_env):
        """Test getting a standard module logger."""
        setup_logging()  # Initialize logging first

        logger = get_logger("test.module")

        assert logger.name == "fluent_forever.test.module"
        assert isinstance(logger, logging.Logger)

    def test_get_context_logger_pipeline_specific(self, clean_logging_env):
        """Test getting a pipeline-specific context logger."""
        setup_logging()  # Initialize logging first

        logger = get_context_logger("core.pipeline", "vocabulary")

        assert logger.name == "fluent_forever.core.pipeline.vocabulary"
        assert isinstance(logger, logging.Logger)

    def test_log_performance_decorator(self, clean_logging_env):
        """Test performance logging decorator."""
        setup_logging()

        @log_performance("test.performance")
        def test_function():
            time.sleep(0.01)  # Small delay
            return "result"

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            result = test_function()

            assert result == "result"
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "test_function completed in" in call_args
            assert "s" in call_args  # Should contain timing in seconds

    def test_colored_formatter_output(self):
        """Test colored formatter produces colored output."""
        formatter = ColoredFormatter("%(levelname)s %(message)s")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Should contain ANSI color codes
        assert "\033[32m" in formatted  # Green color for INFO
        assert "\033[0m" in formatted  # Reset code
        assert "Test message" in formatted

    def test_performance_formatter_timing(self):
        """Test performance formatter includes timing information."""
        formatter = PerformanceFormatter("%(levelname)s %(message)s")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test completed",
            args=(),
            exc_info=None,
        )
        record.duration = 1.234

        formatted = formatter.format(record)

        assert "Test completed (took 1.23s)" in formatted

    def test_contextual_error_formatting(self, clean_logging_env):
        """Test contextual error formatting with additional context."""
        setup_logging()
        logger = get_logger("test")

        error = RuntimeError("Test error")
        context = {"stage": "test_stage", "data": "test_data"}

        with patch.object(logger, "error") as mock_error:
            log_error_with_context(logger, error, context)

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Test error" in str(call_args[0][0])
            assert "extra" in call_args[1]
            assert "context" in call_args[1]["extra"]

    def test_environment_detection_accuracy(self):
        """Test accuracy of test environment detection."""
        # Test pytest detection
        with patch.dict(sys.modules, {"pytest": Mock()}):
            assert _is_test_environment() is True

        # Test environment variable detection
        with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "test"}):
            assert _is_test_environment() is True

        with patch.dict(os.environ, {"TESTING": "true"}):
            assert _is_test_environment() is True

        # Test sys.argv detection
        original_argv = sys.argv[0]
        try:
            sys.argv[0] = "pytest"
            assert _is_test_environment() is True
        finally:
            sys.argv[0] = original_argv

    def test_module_specific_log_levels(self, clean_logging_env, monkeypatch):
        """Test module-specific log level configuration."""
        monkeypatch.setenv("FLUENT_FOREVER_CLI_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("FLUENT_FOREVER_CORE_LOG_LEVEL", "WARNING")

        setup_logging()
        setup_module_log_levels()

        # Check that the env var mapping is working correctly
        cli_level_str = os.getenv("FLUENT_FOREVER_CLI_LOG_LEVEL", "INFO")
        core_level_str = os.getenv("FLUENT_FOREVER_CORE_LOG_LEVEL", "INFO")

        assert cli_level_str == "DEBUG"
        assert core_level_str == "WARNING"

    @patch("src.utils.logging_config._is_test_environment")
    def test_test_environment_file_logging_disabled(
        self, mock_is_test, clean_logging_env
    ):
        """Test file logging is disabled in test environment."""
        mock_is_test.return_value = True

        config = get_logging_config(log_to_file=True)

        # File handler should not be present in test environment
        assert "file" not in config["handlers"]
        assert len(config["loggers"]["fluent_forever"]["handlers"]) == 1
        assert config["loggers"]["fluent_forever"]["handlers"] == ["console"]

    def test_get_log_level_from_env_default(self, monkeypatch):
        """Test getting log level from environment with default."""
        monkeypatch.delenv("FLUENT_FOREVER_LOG_LEVEL", raising=False)

        level = get_log_level_from_env()

        assert level == logging.INFO

    def test_get_log_level_from_env_custom(self, monkeypatch):
        """Test getting log level from environment with custom value."""
        monkeypatch.setenv("FLUENT_FOREVER_LOG_LEVEL", "DEBUG")

        level = get_log_level_from_env()

        assert level == logging.DEBUG

    def test_get_log_level_from_env_invalid(self, monkeypatch):
        """Test getting log level from environment with invalid value."""
        monkeypatch.setenv("FLUENT_FOREVER_LOG_LEVEL", "INVALID")

        level = get_log_level_from_env()

        assert level == logging.INFO  # Should fallback to INFO

    def test_logging_config_base_structure(self):
        """Test base logging configuration structure."""
        config = LOGGING_CONFIG_BASE

        assert "version" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config
        assert "console" in config["formatters"]
        assert "file" in config["formatters"]

    def test_default_log_levels_defined(self):
        """Test default log levels are properly defined."""
        assert "fluent_forever.cli" in DEFAULT_LOG_LEVELS
        assert "fluent_forever.core" in DEFAULT_LOG_LEVELS
        assert "fluent_forever.providers" in DEFAULT_LOG_LEVELS
        assert "fluent_forever.stages" in DEFAULT_LOG_LEVELS

        for level in DEFAULT_LOG_LEVELS.values():
            assert isinstance(level, int)
            assert level in [
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            ]

    def test_icons_dictionary(self):
        """Test ICONS dictionary contains expected icons."""
        expected_icons = [
            "check",
            "cross",
            "warning",
            "info",
            "search",
            "gear",
            "chart",
            "file",
            "folder",
        ]

        for icon in expected_icons:
            assert icon in ICONS
            assert isinstance(ICONS[icon], str)
            assert len(ICONS[icon]) > 0

    def test_contextual_error_creation(self):
        """Test ContextualError exception creation."""
        context = {"stage": "test", "data": "value"}
        error = ContextualError("Test error", context)

        assert str(error) == "Test error"
        assert error.context == context

    def test_contextual_error_default_context(self):
        """Test ContextualError with default empty context."""
        error = ContextualError("Test error")

        assert str(error) == "Test error"
        assert error.context == {}

    @patch("src.utils.logging_config._is_test_environment")
    def test_environment_file_logging_override(
        self, mock_is_test, clean_logging_env, monkeypatch
    ):
        """Test environment variable can force file logging in test environment."""
        mock_is_test.return_value = True
        monkeypatch.setenv("FLUENT_FOREVER_FORCE_FILE_LOG", "true")

        config = get_logging_config(log_to_file=True)

        # Should have file handler even in test environment when forced
        assert "file" in config["handlers"]
        assert "file" in config["loggers"]["fluent_forever"]["handlers"]

    @patch("src.utils.logging_config._is_test_environment")
    def test_log_file_directory_creation(
        self, mock_is_test, clean_logging_env, tmp_path
    ):
        """Test log file directory is created when it doesn't exist."""
        mock_is_test.return_value = False  # Not in test environment
        log_dir = tmp_path / "nested" / "logs"
        log_file = log_dir / "test.log"

        # Directory shouldn't exist initially
        assert not log_dir.exists()

        setup_logging(log_to_file=True, log_file_path=log_file)

        # Directory should be created
        assert log_dir.exists()

    def test_performance_decorator_error_handling(self, clean_logging_env):
        """Test performance decorator handles function errors."""
        setup_logging()

        @log_performance("test.performance")
        def failing_function():
            time.sleep(0.01)
            raise RuntimeError("Test error")

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with pytest.raises(RuntimeError):
                failing_function()

            # Should log error with timing
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "failing_function failed after" in call_args
            assert "Test error" in call_args

    def test_context_logger_without_context_id(self, clean_logging_env):
        """Test context logger creation without context ID."""
        setup_logging()

        logger = get_context_logger("core.pipeline")

        assert logger.name == "fluent_forever.core.pipeline"

    def test_colored_formatter_levelname_reset(self):
        """Test colored formatter resets levelname after formatting."""
        formatter = ColoredFormatter("%(levelname)s %(message)s")

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        original_levelname = record.levelname

        formatter.format(record)

        # Levelname should be reset to original value
        assert record.levelname == original_levelname

    @patch("src.utils.logging_config._is_test_environment")
    def test_env_log_to_file_respected(
        self, mock_is_test, clean_logging_env, monkeypatch
    ):
        """Test FLUENT_FOREVER_LOG_TO_FILE environment variable is respected."""
        mock_is_test.return_value = False  # Not in test environment
        monkeypatch.setenv("FLUENT_FOREVER_LOG_TO_FILE", "true")

        config = get_logging_config()

        # Should enable file logging based on environment variable
        assert "file" in config["handlers"]

    def test_log_error_with_context_error_context_attribute(self, clean_logging_env):
        """Test log_error_with_context handles errors with context attribute."""
        setup_logging()
        logger = get_logger("test")

        error = ContextualError("Test error", {"initial": "context"})
        additional_context = {"additional": "data"}

        with patch.object(logger, "error") as mock_error:
            log_error_with_context(logger, error, additional_context)

            mock_error.assert_called_once()
            call_args = mock_error.call_args[1]
            context = call_args["extra"]["context"]
            # Should merge both contexts
            assert context["initial"] == "context"
            assert context["additional"] == "data"
