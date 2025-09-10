#!/usr/bin/env python3
"""
Logging Configuration
Centralized logging setup for the Fluent Forever v2 system
"""

import functools
import logging
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        # Format the message
        formatted = super().format(record)

        # Reset levelname for other formatters
        record.levelname = levelname

        return formatted


def setup_logging(
    level: int | None = None,
    log_to_file: bool = False,
    log_file_path: Path | None = None,
) -> logging.Logger:
    """
    Set up logging configuration

    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to also log to file
        log_file_path: Path for log file (default: project_root/logs/fluent_forever.log)

    Returns:
        Configured logger
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get level from environment if not specified
    if level is None:
        level = get_log_level_from_env()

    # Create logger
    logger = logging.getLogger("fluent_forever")
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Colored formatter for console
    console_format = "%(levelname)s %(message)s"
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        if log_file_path is None:
            project_root = Path(__file__).parent.parent.parent
            log_file_path = project_root / "logs" / "fluent_forever.log"

        # Create logs directory if it doesn't exist
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)

        # Plain formatter for file (no colors)
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Setup module-specific log levels
    setup_module_log_levels()

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module

    Args:
        module_name: Name of the module (e.g., 'anki.connection')

    Returns:
        Module-specific logger
    """
    return logging.getLogger(f"fluent_forever.{module_name}")


def get_context_logger(
    module_name: str, context_id: str | None = None
) -> logging.Logger:
    """
    Get a context-aware logger for a specific module and context

    Args:
        module_name: Name of the module (e.g., 'core.pipeline')
        context_id: Optional context identifier (e.g., pipeline name)

    Returns:
        Context-specific logger
    """
    logger_name = f"fluent_forever.{module_name}"
    if context_id:
        logger_name += f".{context_id}"
    return logging.getLogger(logger_name)


def get_log_level_from_env() -> int:
    """Get log level from environment variable"""
    level_str = os.getenv("FLUENT_FOREVER_LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_str, logging.INFO)


def setup_module_log_levels() -> None:
    """Configure module-specific log levels from environment"""
    for module, default_level in DEFAULT_LOG_LEVELS.items():
        env_var = f"FLUENT_FOREVER_{module.replace('.', '_').upper()}_LOG_LEVEL"
        level_str = os.getenv(env_var, logging.getLevelName(default_level))
        level = getattr(logging, level_str.upper(), default_level)
        logging.getLogger(module).setLevel(level)


def log_performance(logger_name: str | None = None) -> Callable:
    """Decorator for logging performance timing"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(
                logger_name or f"fluent_forever.performance.{func.__name__}"
            )
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: dict | None = None
) -> None:
    """Log an error with additional context information"""
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **(context or {}),
    }

    if hasattr(error, "context"):
        error_context.update(error.context)

    logger.error(f"{ICONS['cross']} {error}", extra={"context": error_context})


# Default log levels for different modules
DEFAULT_LOG_LEVELS = {
    "fluent_forever.cli": logging.INFO,
    "fluent_forever.core": logging.INFO,
    "fluent_forever.providers": logging.INFO,
    "fluent_forever.stages": logging.INFO,
}


# Icons for common log messages
ICONS = {
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "search": "🔍",
    "gear": "🔧",
    "chart": "📊",
    "file": "📄",
    "folder": "📁",
}


class PerformanceFormatter(ColoredFormatter):
    """Formatter that includes performance timing information"""

    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "duration"):
            record.msg = f"{record.msg} (took {record.duration:.2f}s)"
        return super().format(record)


class ContextualError(Exception):
    """Exception that carries additional context for logging"""

    def __init__(self, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.context = context or {}
