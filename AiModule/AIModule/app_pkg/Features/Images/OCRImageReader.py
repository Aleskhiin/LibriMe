import asyncio
import shutil
import platform
import cv2
import os
import pytesseract

from .BaseImageReader import BaseImageReader
from app_pkg.Logger.Logging_setup import logger


class OCRImageReader(BaseImageReader):
    """
    OCR reader implementation using Tesseract.
    """

    def __init__(self):
        """
        Initializes the OCR image reader.
        """

        super().__init__()

        self.configure_tesseract()

    def configure_tesseract(self):
        """
        Configures the Tesseract executable path depending
        on the current operating system.
        """

        logger.info(
            "Configure Tesseract OCR for the current operating system."
        )

        system = platform.system()

        if system == "Windows":

            path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

            pytesseract.pytesseract.tesseract_cmd = path

            if not shutil.which(path):
                logger.warning(
                    "Default Tesseract path not found."
                )

        elif system in ["Linux", "Darwin"]:

            tesseract_path = shutil.which("tesseract")

            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path

            else:
                raise FileNotFoundError(
                    "Tesseract not found. "
                    "Please install tesseract-ocr."
                )

        else:
            raise OSError(
                f"Unsupported operating system: {system}"
            )

        logger.info(
            "Successfully configured Tesseract."
        )

    def load_image(self):
        """
        Loads an image and converts it to RGB.

        Returns:
            Tuple containing:
            - original image
            - RGB image
        """

        if not self.file_path:
            raise ValueError(
                "Image file path not configured."
            )

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Image not found: {self.file_path}"
            )

        image = cv2.imread(self.file_path)

        image_rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        return image, image_rgb

    def extract_text(self, image_rgb):
        """
        Extracts text using Tesseract OCR.

        Args:
            image_rgb: RGB image.

        Returns:
            Extracted text.
        """

        logger.info(
            "Start OCR text extraction."
        )

        return pytesseract.image_to_string(
            image_rgb
        )

    async def process(self):
        """
        Executes the OCR workflow.

        Returns:
            Extracted text.
        """

        logger.info(
            f"Start OCR processing for "
            f"{self.file_path}"
        )

        image_rgb = self.load_image()[1]

        text = self.extract_text(image_rgb)

        logger.info(
            f"Successfully extracted text from "
            f"{self.file_path}"
        )

        return text