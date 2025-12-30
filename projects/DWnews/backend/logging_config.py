"""
The Daily Worker - Logging Configuration
Configures structured logging for the application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from config import settings


def setup_logging():
    """Configure application logging with console and file handlers"""

    # Create logs directory if it doesn't exist
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler (formatted for human readability)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))

    if settings.debug:
        # Detailed format for development
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Simpler format for production
        console_format = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (JSON format for structured logging)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    # JSON formatter for structured logs
    json_format = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    file_handler.setFormatter(json_format)
    logger.addHandler(file_handler)

    # Log startup message
    logger.info(
        "Logging initialized",
        extra={
            "environment": settings.environment,
            "log_level": settings.log_level,
            "log_file": settings.log_file
        }
    )

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)


# Initialize logging when module is imported
if __name__ != "__main__":
    setup_logging()
