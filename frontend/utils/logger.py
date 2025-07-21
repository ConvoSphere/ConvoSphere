"""
Centralized logging module for the frontend application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str = "convosphere",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup and configure the application logger.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        use_colors: Whether to use colored output
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if use_colors:
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"convosphere.{name}")


# Convenience functions for common logging operations
def log_info(message: str, logger_name: str = None):
    """Log an info message."""
    if logger_name:
        get_logger(logger_name).info(message)
    else:
        logger.info(message)


def log_warning(message: str, logger_name: str = None):
    """Log a warning message."""
    if logger_name:
        get_logger(logger_name).warning(message)
    else:
        logger.warning(message)


def log_error(message: str, logger_name: str = None, exc_info: bool = False):
    """Log an error message."""
    if logger_name:
        get_logger(logger_name).error(message, exc_info=exc_info)
    else:
        logger.error(message, exc_info=exc_info)


def log_debug(message: str, logger_name: str = None):
    """Log a debug message."""
    if logger_name:
        get_logger(logger_name).debug(message)
    else:
        logger.debug(message)


def log_critical(message: str, logger_name: str = None, exc_info: bool = False):
    """Log a critical message."""
    if logger_name:
        get_logger(logger_name).critical(message, exc_info=exc_info)
    else:
        logger.critical(message, exc_info=exc_info)