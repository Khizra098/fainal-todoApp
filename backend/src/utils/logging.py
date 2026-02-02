"""
Logging utilities for the AI Assistant Chat feature.
This module contains centralized logging configuration and functions.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json

# Create a custom formatter that includes timestamps and levels
class CustomFormatter(logging.Formatter):
    """Custom formatter to add colors and format to logs"""

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Set up the main logger for the chat application
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter and add it to the handlers
    formatter = CustomFormatter()
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)

    return logger


def log_chat_interaction(user_id: str, conversation_id: str, message_content: str,
                        response_content: str, processing_time: float) -> None:
    """
    Log a chat interaction with relevant details
    """
    logger = setup_logger("chat.interaction")

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message_content": message_content[:100] + "..." if len(message_content) > 100 else message_content,  # Truncate long messages
        "response_content": response_content[:100] + "..." if len(response_content) > 100 else response_content,
        "processing_time_ms": processing_time
    }

    logger.info(f"Chat interaction: {json.dumps(log_data)}")


def log_error(error: Exception, context: str = "") -> None:
    """
    Log an error with context
    """
    logger = setup_logger("chat.error")
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_performance(metric: str, value: float, unit: str = "") -> None:
    """
    Log performance metrics
    """
    logger = setup_logger("chat.performance")
    unit_str = f" {unit}" if unit else ""
    logger.info(f"Performance metric - {metric}: {value}{unit_str}")


# Set up the main application logger
app_logger = setup_logger("chat.app")