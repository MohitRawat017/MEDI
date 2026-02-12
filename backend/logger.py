"""
Logger Module: Centralized logging configuration for the application
"""

import logging


def setup_logger(name="Medical-Assistant"):
    """
    Set up and configure a logger for the application.

    Args:
        name (str): Logger name (default: "Medical-Assistant")

    Returns:
        logging.Logger: Configured logger instance

    Configuration:
        - Level: DEBUG (logs all messages)
        - Handler: FileHandler writing to app.log
        - Format: timestamp - logger_name - level - message
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # File handler for logging to app.log
    ch = logging.FileHandler("app.log")
    ch.setLevel(logging.DEBUG)

    # Format: timestamp - name - level - message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)

    # Avoid duplicate handlers if logger is reconfigured
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger

