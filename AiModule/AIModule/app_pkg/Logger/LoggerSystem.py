
from ConfigurableLogger import ConfigurableLogger
import logging


class LoggerSystem:
    """
    Convenience wrapper around `ConfigurableLogger`.

    This class simplifies logger initialization and provides
    lightweight helper methods for common log levels.
    """


    def __init__(self, log_dir="logs", retention_days=5, log_filename="hackathon.log"):      
        """
        Initializes the logging system.

        Args:
            log_dir: Directory where log files are stored.
            retention_days: Number of days log files are retained.
            log_filename: Name of the main log file.
        """
        self.logger = self._initialize_logger(log_dir, retention_days, log_filename)

    def _initialize_logger(self, log_dir, retention_days, log_filename):  
        """
        Creates and configures the underlying logger instance.

        Returns:
            Configured `logging.Logger` instance.
        """
        return ConfigurableLogger(
            name="LibriMeLog_AI_module",
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
    log_system = LoggerSystem(log_dir="logs", retention_days=5, log_filename="libriMe_AI_module_main.log")
    log_system.log_info("System started.")
    log_system.log_debug("Debugging mode active.")
    log_system.log_error("An error occurred.")


if __name__ == "__main__":
    main()
