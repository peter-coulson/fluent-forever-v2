#!/usr/bin/env python3
"""
Logging Configuration
Centralized logging setup for the Fluent Forever v2 system
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname for other formatters
        record.levelname = levelname
        
        return formatted

def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file_path: Optional[Path] = None
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
    # Create logger
    logger = logging.getLogger('fluent_forever')
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Colored formatter for console
    console_format = '%(levelname)s %(message)s'
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        if log_file_path is None:
            project_root = Path(__file__).parent.parent.parent
            log_file_path = project_root / 'logs' / 'fluent_forever.log'
        
        # Create logs directory if it doesn't exist
        log_file_path.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        
        # Plain formatter for file (no colors)
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        module_name: Name of the module (e.g., 'anki.connection')
    
    Returns:
        Module-specific logger
    """
    return logging.getLogger(f'fluent_forever.{module_name}')

# Icons for common log messages
ICONS = {
    'check': '✅',
    'cross': '❌', 
    'warning': '⚠️',
    'info': 'ℹ️',
    'search': '🔍',
    'gear': '🔧',
    'chart': '📊',
    'file': '📄',
    'folder': '📁'
}