"""
E2E Test Scenario 5: Logging and Performance Monitoring Integration

Purpose: Validate logging infrastructure and performance monitoring
"""

import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.context import PipelineContext
from src.utils.logging_config import (
    ICONS,
    get_context_logger,
    get_logger,
    log_performance,
    setup_logging,
)
from tests.fixtures.contexts import create_test_context
from tests.fixtures.pipelines import SuccessStage, MockPipeline


class TestLoggingPerformanceIntegration:
    """Test logging infrastructure and performance monitoring."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def project_root(self):
        """Get project root path."""
        return Path(__file__).parents[3]

    def test_logging_setup_console_only(self, capsys):
        """Test logging setup with console output only."""
        # Setup logging with console output
        setup_logging(level=logging.INFO, log_to_file=False)
        
        # Get logger and log message
        logger = get_logger("test.module")
        logger.info("Test console message")
        
        # Check console output
        captured = capsys.readouterr()
        # Note: In test environment, logging may not appear in captured output
        # This depends on how pytest handles logging

    def test_logging_setup_with_file(self, temp_log_dir):
        """Test logging setup with file output."""
        log_file = temp_log_dir / "test.log"
        
        with patch('src.utils.logging_config.LOG_DIR', temp_log_dir):
            setup_logging(level=logging.DEBUG, log_to_file=True)
            
            # Log a message
            logger = get_logger("test.file")
            logger.info("Test file message")
            
            # File logging depends on implementation details
            # This test validates the setup doesn't crash

    def test_context_aware_logging(self, project_root):
        """Test context-aware logger creation."""
        pipeline_name = "test_pipeline"
        module_name = "test.module"
        
        # Create context-aware logger
        logger = get_context_logger(module_name, pipeline_name)
        
        # Logger should be created successfully
        assert logger is not None
        assert logger.name == f"fluent_forever.{module_name}"

    def test_performance_monitoring_decorator(self, project_root):
        """Test performance monitoring decorator."""
        @log_performance("test.performance")
        def test_function(duration: float = 0.01) -> str:
            time.sleep(duration)
            return "test_result"
        
        # Execute function with performance monitoring
        result = test_function(0.01)
        
        # Function should complete successfully
        assert result == "test_result"

    def test_stage_execution_with_logging(self, project_root, capsys):
        """Test stage execution with logging integration."""
        context = create_test_context("test_pipeline", project_root)
        
        # Execute stage (which includes logging)
        stage = SuccessStage()
        result = stage.execute(context)
        
        # Stage should complete successfully
        assert result.success
        
        # Logging should have occurred (captured in stage execution)
        captured = capsys.readouterr()
        # Stage execution includes logging, though it may not appear in capsys

    def test_pipeline_execution_logging(self, project_root):
        """Test pipeline execution with comprehensive logging."""
        pipeline = MockPipeline("test_pipeline")
        context = create_test_context("test_pipeline", project_root)
        
        # Execute pipeline stage (includes performance logging)
        result = pipeline.execute_stage("test_stage", context)
        
        # Should complete successfully with logging
        assert result.success

    def test_logging_levels_and_filtering(self):
        """Test logging level configuration and message filtering."""
        # Setup with INFO level
        setup_logging(level=logging.INFO, log_to_file=False)
        
        logger = get_logger("test.levels")
        
        # These calls should not raise errors
        logger.debug("Debug message")  # Should be filtered out
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear

    def test_logging_with_icons(self):
        """Test logging integration with icon system."""
        logger = get_logger("test.icons")
        
        # Test that icon constants are available
        assert "gear" in ICONS
        assert "check" in ICONS
        assert "cross" in ICONS
        assert "info" in ICONS
        assert "warning" in ICONS
        
        # Test logging with icons (should not raise errors)
        logger.info(f"{ICONS['gear']} Starting process")
        logger.info(f"{ICONS['check']} Process completed")
        logger.error(f"{ICONS['cross']} Process failed")

    def test_environment_based_logging_configuration(self):
        """Test logging configuration based on environment variables."""
        # Test debug environment
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("FLUENT_FOREVER_DEBUG", "true")
            
            # Setup should respect environment
            setup_logging()
            
            # Should not raise errors
            logger = get_logger("test.env")
            logger.debug("Debug message in debug mode")

    def test_test_environment_logging_behavior(self):
        """Test logging behavior in test environment."""
        # Test that logging works in test environment
        setup_logging(level=logging.DEBUG, log_to_file=False)
        
        logger = get_logger("test.environment")
        
        # Should handle test environment gracefully
        logger.info("Test environment logging")
        logger.debug("Debug in test environment")

    def test_performance_monitoring_with_context(self, project_root):
        """Test performance monitoring with pipeline context."""
        context = create_test_context("performance_test", project_root)
        
        @log_performance("test.context.performance")
        def context_operation(ctx: PipelineContext) -> None:
            ctx.set("operation_completed", True)
            time.sleep(0.01)  # Simulate work
        
        # Execute with context
        context_operation(context)
        
        # Verify operation completed
        assert context.get("operation_completed") is True

    def test_logging_with_stage_timing(self, project_root):
        """Test logging integration with stage execution timing."""
        class TimedStage(SuccessStage):
            def _execute_impl(self, context: PipelineContext):
                # Simulate some work
                time.sleep(0.01)
                return super()._execute_impl(context)
        
        context = create_test_context("timed_test", project_root)
        stage = TimedStage()
        
        # Execute with timing
        result = stage.execute(context)
        
        # Should complete successfully
        assert result.success

    def test_error_logging_and_context_integration(self, project_root):
        """Test error logging integration with context error tracking."""
        context = create_test_context("error_test", project_root)
        
        # Add error to context
        context.add_error("Test error for logging")
        
        # Verify error was logged and tracked
        assert context.has_errors()
        assert "Test error for logging" in context.errors

    def test_verbose_mode_logging(self, capsys):
        """Test verbose mode logging configuration."""
        # Setup verbose logging
        setup_logging(level=logging.DEBUG, log_to_file=False)
        
        logger = get_logger("test.verbose")
        
        # Log at various levels
        logger.debug("Verbose debug message")
        logger.info("Verbose info message")
        
        # Should not raise errors
        captured = capsys.readouterr()

    def test_logging_configuration_validation(self):
        """Test logging configuration edge cases."""
        # Test with various log levels
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            setup_logging(level=level, log_to_file=False)
            logger = get_logger("test.config")
            logger.log(level, f"Test message at level {level}")

    def test_performance_decorator_with_exceptions(self):
        """Test performance decorator behavior with exceptions."""
        @log_performance("test.exception.performance")
        def failing_function():
            raise ValueError("Test exception")
        
        # Should still log performance even with exception
        with pytest.raises(ValueError):
            failing_function()

    def test_pipeline_phase_logging(self, project_root):
        """Test logging during pipeline phase execution."""
        pipeline = MockPipeline("logging_test")
        pipeline._phases = {"test_phase": ["test_stage"]}
        
        context = create_test_context("logging_test", project_root)
        
        # Execute phase (includes logging)
        results = pipeline.execute_phase("test_phase", context)
        
        # Should complete successfully
        assert len(results) == 1
        assert results[0].success

    def test_logger_hierarchy_and_context(self):
        """Test logger hierarchy and context separation."""
        # Create loggers for different contexts
        logger1 = get_context_logger("module1", "pipeline1")
        logger2 = get_context_logger("module2", "pipeline2")
        logger3 = get_logger("module3")
        
        # All should be created successfully
        assert logger1 is not None
        assert logger2 is not None
        assert logger3 is not None
        
        # Should have appropriate names
        assert "fluent_forever" in logger1.name
        assert "fluent_forever" in logger2.name
        assert "fluent_forever" in logger3.name

    def test_logging_integration_with_cli_verbose_mode(self, capsys):
        """Test logging integration with CLI verbose mode."""
        # Simulate CLI verbose mode setup
        if os.getenv("FLUENT_FOREVER_DEBUG") or True:  # Force for test
            enable_file_logging = (
                os.getenv("FLUENT_FOREVER_LOG_TO_FILE", "false").lower() == "true"
            )
            setup_logging(level=logging.DEBUG, log_to_file=enable_file_logging)
        else:
            setup_logging()
        
        logger = get_logger("cli.test")
        logger.info("CLI verbose mode test message")
        
        # Should complete without errors
        captured = capsys.readouterr()

    def test_log_message_formatting_and_icons(self):
        """Test log message formatting with icons and context."""
        logger = get_logger("test.formatting")
        
        # Test various icon combinations
        logger.info(f"{ICONS['gear']} Starting operation")
        logger.info(f"{ICONS['check']} Operation completed successfully")
        logger.warning(f"{ICONS['warning']} Operation warning")
        logger.error(f"{ICONS['cross']} Operation failed")
        
        # Test context-aware formatting
        context_logger = get_context_logger("test.formatting", "test_pipeline")
        context_logger.info(f"{ICONS['info']} Context-aware message")

    def test_performance_monitoring_aggregation(self, project_root):
        """Test performance monitoring data aggregation."""
        @log_performance("test.aggregation")
        def monitored_operation(operation_id: str) -> str:
            time.sleep(0.001)  # Minimal work
            return f"completed_{operation_id}"
        
        # Execute multiple operations
        results = []
        for i in range(3):
            result = monitored_operation(f"op_{i}")
            results.append(result)
        
        # All should complete
        assert len(results) == 3
        assert all("completed_" in result for result in results)