"""
This file configures the logging system for the application, allowing logs to be recorded
both to the console and a log file. This setup ensures that real-time logs can be seen 
during development and debugging, and a persistent record of logs is maintained for later 
analysis. This is particularly useful when the application is running in a Docker container.
"""

import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # Prevents the disabling of existing logger
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",   # Handler class to write logs to a file
            "formatter": "default",
            "filename": "/app/logs/app.log", # Log file path
            "mode": "a", # Appending mode to add logs to the existing file
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"],
    },
}

def setup_logging():
    dictConfig(LOGGING_CONFIG)
