import logging
from datetime import datetime
from typing import Optional

class PreciseFormatter(logging.Formatter):
    """
    Custom logging formatter that produces timestamps with a configurable
    number of fractional second digits derived from microseconds.

    Example output:
        [2026-01-07 19:30:24.3550] <INFO> Message
    """

    def __init__(
        self,
        fmt: str,
        datefmt: Optional[str] = None,
        fraction_digits: int = 4
    ):
        """
        Args:
            fmt: Log format string (e.g. "[%(asctime)s] <%(levelname)s> %(message)s")
            datefmt: Optional date format (unused, custom formatting is applied)
            fraction_digits: Number of fractional second digits (1–6)
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
        # Clamp fractional digits to a valid microsecond range
        self.fraction_digits = max(1, min(6, fraction_digits))

    def formatTime(self, record, datefmt=None) -> str:
        """
        Formats the log record timestamp with sub‑second precision.

        Args:
            record: The logging record
            datefmt: Optional date format (ignored)

        Returns:
            Formatted timestamp string
        """
        # record.created is seconds since epoch (float)
        dt = datetime.fromtimestamp(record.created)

        # Base timestamp without sub‑seconds
        base = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Microseconds trimmed to the requested precision
        micros = f"{dt.microsecond:06d}"[:self.fraction_digits]

        return f"{base}.{micros}"