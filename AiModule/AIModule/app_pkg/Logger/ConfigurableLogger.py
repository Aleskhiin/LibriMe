
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


class PreciseFormatter(logging.Formatter):
    """
    Formatter, der einen Zeitstempel mit frei wählbarer Anzahl Nachkommastellen
    (aus Mikrosekunden) erzeugt, z. B. [2026-01-07 19:30:24.3550].
    """

    def __init__(self, fmt: str, datefmt: Optional[str] = None, fraction_digits: int = 4):
        # fmt z. B.: "[%(asctime)s] <%(levelname)s> %(message)s"
        super().__init__(fmt=fmt, datefmt=datefmt)
        # Anzahl Nachkommastellen (1–6), da wir aus %f (Mikrosekunden, 6 Stellen) schneiden
        self.fraction_digits = max(1, min(6, fraction_digits))

    def formatTime(self, record, datefmt=None) -> str:
        # record.created ist ein float (Sekunden seit Epoch)
        dt = datetime.fromtimestamp(record.created)
        # Basis ohne Nachkommastellen
        base = dt.strftime("%Y-%m-%d %H:%M:%S")
        # Mikrosekunden (6-stellig), auf gewünschte Länge gekürzt
        micros = f"{dt.microsecond:06d}"[:self.fraction_digits]
        return f"{base}.{micros}"


class ConfigurableLogger:
    """
    Konfigurierbarer Logger mit:
    - Konsolen- und Datei-Handler
    - täglicher Rotation (Mitternacht)
    - Aufbewahrung (retention_days)
    - Zeitstempel: [YYYY-MM-DD HH:MM:SS.xxxx] <LEVEL> Nachricht
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
        fraction_digits: int = 4,  # Anzahl Nachkommastellen im Zeitstempel
        use_local_time: bool = True,
    ):
        """
        Args:
            name: interner Logger-Name.
            level: z. B. logging.INFO / logging.DEBUG.
            log_dir: Zielverzeichnis der Logs.
            log_filename: Dateiname (z. B. 'hackathon.log').
            retention_days: wie lange Logdateien aufbewahrt werden.
            enable_console: zusätzlich auf die Konsole loggen.
            propagate: Weitergabe an Root-Logger.
            when: Rotationsintervall (z. B. 'midnight', 'D', 'H').
            backup_count: Anzahl Rotationen, die TimedRotatingFileHandler behält
                          (wir löschen zusätzlich altersbasiert).
            encoding: Dateicodierung.
            fraction_digits: Anzahl Nachkommastellen (1–6).
            use_local_time: True = lokale Zeit, False = UTC für Rotation.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = propagate

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_filename)

        # Minimal gewünschtes Format: Datum/Zeit + Level in <>
        fmt = "[%(asctime)s] <%(levelname)s> %(message)s"

        # Doppelte Handler vermeiden
        if not self.logger.handlers:
            formatter = PreciseFormatter(fmt=fmt, fraction_digits=fraction_digits)

            # Konsole
            if enable_console:
                ch = logging.StreamHandler()
                ch.setLevel(level)
                ch.setFormatter(formatter)
                self.logger.addHandler(ch)

            # Datei mit täglicher Rotation
            fh = TimedRotatingFileHandler(
                filename=log_path,
                when=when,
                interval=1,
                backupCount=backup_count,
                encoding=encoding,
                utc=not use_local_time,
            )
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

            # Aufbewahrung sofort anwenden
            self._apply_retention(log_dir, retention_days)

            # Nach jeder Rotation erneut anwenden
            original_rollover = fh.doRollover

            def patched_rollover():
                original_rollover()
                try:
                    self._apply_retention(log_dir, retention_days)
                except Exception as e:
                    # Retention-Fehler sollen das Logging nicht unterbrechen
                    self.logger.debug(f"Retention pruning failed: {e}")

            fh.doRollover = patched_rollover

    @staticmethod
    def _apply_retention(log_dir: str, retention_days: int) -> None:
        """
        Löscht Logdateien im log_dir, die älter als retention_days sind.
        Berücksichtigt typische Rotationsdateien (z. B. app.log, app.log.YYYY-MM-DD).
        """
        if retention_days is None or retention_days <= 0:
            return

        cutoff = datetime.now() - timedelta(days=retention_days)

        for entry in os.scandir(log_dir):
            if not entry.is_file():
                continue
            name = entry.name
            if not name.endswith(".log") and ".log." not in name:
                continue
            try:
                mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                if mtime < cutoff:
                    os.remove(entry.path)
            except Exception:
                continue
