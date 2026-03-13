from .ConfigurableLogger import ConfigurableLogger
import logging

logger = ConfigurableLogger(
    name="Librime",
    log_dir="logs",
    log_filename="Librime.log",
    retention_days=5,
    enable_console=True,
    fraction_digits=4,
    level=logging.INFO,
).logger
