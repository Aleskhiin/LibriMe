
from ConfigurableLogger import ConfigurableLogger
import logging


class LoggerSystem:
    """
    Wrapper-Klasse zum Einrichten und Verwenden des konfigurierbaren Loggers.
    """

    def __init__(self, log_dir="logs", retention_days=5, log_filename="hackathon.log"):
        self.logger = self._initialize_logger(log_dir, retention_days, log_filename)

    def _initialize_logger(self, log_dir, retention_days, log_filename):
        return ConfigurableLogger(
            name="hackathon",
            level=logging.INFO,
            log_dir=log_dir,
            log_filename=log_filename,
            retention_days=retention_days,
            enable_console=True,
            fraction_digits=4,  # exakt vier Nachkommastellen wie in deinem Beispiel
        ).logger

    def log_info(self, message):  self.logger.info(message)
    def log_error(self, message): self.logger.error(message)
    def log_debug(self, message): self.logger.debug(message)


def main():
    log_system = LoggerSystem(log_dir="logs", retention_days=5, log_filename="hackathon.log")
    log_system.log_info("System started.")
    log_system.log_debug("Debugging mode active.")
    log_system.log_error("An error occurred.")


if __name__ == "__main__":
    main()
