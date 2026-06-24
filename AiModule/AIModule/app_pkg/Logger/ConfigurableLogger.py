import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from .PreciseFormatter import PreciseFormatter
from typing import Optional


class ConfigurableLogger:
    """
    Fully configurable logger utility that provides:

    - Console and file logging
    - Time‑based file rotation (default: daily at midnight)
    - Optional log retention by age (day‑based)
    - High‑resolution timestamps with fractional seconds
    - Optional UTC or local time handling

    The resulting log format is:
        [YYYY-MM-DD HH:MM:SS.xxxx] <LEVEL> Message
    """

    def __init__(
        self,
        name: str = "app",
        level: int = logging.INFO,
        log_dir: str = "logs",
        log_filename: str = "app.log",
        retention_days: int = 7,
        enable_console: bool = True,
        propagate: bool = False,
        when: str = "midnight",
        backup_count: int = 0,
        encoding: Optional[str] = "utf-8",
        fraction_digits: int = 4,
        use_local_time: bool = True,
    ):
        """
        Initializes a configurable logger with console and file logging,
        time‑based rotation, retention cleanup, and high‑precision timestamps.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = propagate

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_filename)

        if not self.logger.handlers:
            file_handler = self._create_handlers(
                level=level,
                log_path=log_path,
                enable_console=enable_console,
                when=when,
                backup_count=backup_count,
                encoding=encoding,
                fraction_digits=fraction_digits,
                use_local_time=use_local_time,
            )

            self._setup_file_rotation_and_retention(
                file_handler=file_handler,
                log_dir=log_dir,
                retention_days=retention_days,
            )

    
    def _create_handlers(
        self,
        *,
        level: int,
        log_path: str,
        enable_console: bool,
        when: str,
        backup_count: int,
        encoding: Optional[str],
        fraction_digits: int,
        use_local_time: bool,
    ):
        """
        Creates and attaches console and file handlers to the logger.

        Returns:
            TimedRotatingFileHandler: The file handler instance.
        """
        log_format = "[%(asctime)s] <%(levelname)s> %(message)s"

        formatter = PreciseFormatter(
            fmt=log_format,
            fraction_digits=fraction_digits
        )

        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        file_handler = TimedRotatingFileHandler(
            filename=log_path,
            when=when,
            interval=1,
            backupCount=backup_count,
            encoding=encoding,
            utc=not use_local_time,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        return file_handler

    def _setup_file_rotation_and_retention(
        self,
        file_handler: TimedRotatingFileHandler,
        log_dir: str,
        retention_days: int,
    ) -> None:
        original_do_rollover = file_handler.doRollover

        def do_rollover_with_retention():
            original_do_rollover()
            self._apply_retention(log_dir, retention_days)

        file_handler.doRollover = do_rollover_with_retention

    @staticmethod
    def _apply_retention(log_dir: str, retention_days: int) -> None:
        """
        Deletes log files in the given directory that are older than
        the specified retention period.

        This method supports typical rotated log naming schemes such as:
            app.log
            app.log.YYYY-MM-DD

        Args:
            log_dir: Directory containing log files.
            retention_days: Number of days to keep logs.
        """
        if retention_days is None or retention_days <= 0:
            return

        cutoff = datetime.now() - timedelta(days=retention_days)

        for entry in os.scandir(log_dir):
            if not entry.is_file():
                continue

            filename = entry.name
            if not filename.endswith(".log") and ".log." not in filename:
                continue

            try:
                mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                if mtime < cutoff:
                    os.remove(entry.path)
            except Exception:
                # Ignore individual file errors
                continue