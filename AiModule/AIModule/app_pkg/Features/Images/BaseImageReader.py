from abc import abstractmethod
from typing import Optional

from ..BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger


class BaseImageReader(BaseFeature):
    """
    Abstract base class for all image readers.
    """

    def __init__(self):
        """
        Initializes the common image reader configuration.
        """

        self.file_path: Optional[str] = None

    def configure(self, file_path: str):
        """
        Configures the image reader.

        Args:
            file_path: Path to the image file.
        """

        self.file_path = file_path

        logger.info(
            f"Configured {self.__class__.__name__} "
            f"for file: {file_path}"
        )

    @abstractmethod
    def load_image(self):
        """
        Loads the image into memory.
        """
        pass

