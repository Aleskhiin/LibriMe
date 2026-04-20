from .ConfigurableLogger import ConfigurableLogger
import logging

"""
Application-wide logger configuration for LibriMe.

This module initializes a single, shared logger instance using
the ConfigurableLogger utility. It should be imported wherever
logging is required.
"""

logger = ConfigurableLogger(
    name="LibriMeLog_AI_module",
    log_dir="logs",
    log_filename="LibriMeLog_AI_module.log",
    retention_days=5,
    enable_console=True,
    fraction_digits=4,
    level=logging.INFO,
).logger
