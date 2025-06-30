import logging
import os
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_NAME = os.getenv("APP_NAME", "dassyor")


def setup_logging():
    """Configure application logging with console and rotating file handlers"""
    # Create logs directory if it doesn't exist
    logs_dir = "dassyor_logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create file handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(logs_dir, f"{APP_NAME}.log"),
        when="midnight",
        interval=1,
        backupCount=30,  # Keep logs for 30 days
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = (
        "%Y-%m-%d.txt"  # Format for rotated files: dassyor.log.2024-03-21.txt
    )
    root_logger.addHandler(file_handler)

    # Log that logging has been configured
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured successfully. Log files: {logs_dir}/{APP_NAME}.log"
    )

    return root_logger


def get_logger(name: str):
    """Get a logger instance for a specific module

    Args:
        name: Usually __name__ from the calling module

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
