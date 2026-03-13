import asyncio
import shutil
import platform
import cv2
from matplotlib import pyplot as plt
import os
import pytesseract

from .BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger

class OCRFeature(BaseFeature):
    """
    OCRFeature provides functionality to extract text from images using Tesseract OCR.
    It supports automatic configuration of Tesseract based on the operating system.
    """

    def __init__(self):
        """
        Initialize the OCR feature with the given image path and configure Tesseract.
        """
        self.configure_tesseract()

    def configure_tesseract(self):
        """
        Configures the Tesseract executable path based on the operating system.
        Supports Windows, Linux, and macOS.
        Raises:
            FileNotFoundError: If Tesseract is not installed or cannot be found.
        """

        logger.info(f"Set the tessaeract settings for the OS system for the OCR Feature.")
        system = platform.system()

        if system == "Windows":
            # Default installation path for Tesseract on Windows
            path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            pytesseract.pytesseract.tesseract_cmd = path
            if not shutil.which(path):
                logger.warning("Warning: Default Tesseract path not found. Please verify installation.")
                print("Warning: Default Tesseract path not found. Please verify installation.")

        elif system in ["Linux", "Darwin"]:  # Linux or macOS
            tesseract_path = shutil.which("tesseract")
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                logger.error("Tesseract not found. Please install it:\n"
                    "- Linux: sudo apt install tesseract-ocr\n"
                    "- macOS: brew install tesseract")
                raise FileNotFoundError(
                    "Tesseract not found. Please install it:\n"
                    "- Linux: sudo apt install tesseract-ocr\n"
                    "- macOS: brew install tesseract"
                )
        else:
            logger.error(f"Unsupported operating system: {system}")
            raise OSError(f"Unsupported operating system: {system}")
        logger.info("Successfully set the tessaeract settings for the OS system for the OCR Feature.")

    def load_image(self, image_path: str):
        """
        Loads an image from the specified path and converts it to RGB format.
        Args:
            image_path (str): Path to the image file.
        Returns:
            tuple: (original image, RGB image)
        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        logger.info(f"load the image:{image_path} into the system.")
        if not os.path.exists(image_path):
            logger.error(f"Image not found at: {os.path.abspath(image_path)}")
            raise FileNotFoundError(f"Image not found at: {os.path.abspath(image_path)}")
        
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        logger.info(f"Return the image data from the image:{image_path}, for the extracting of the text information.")
        return image, image_rgb

    def extract_text(self, image_rgb):
        """
        Extracts text from an RGB image using Tesseract OCR.
        Args:
            image_rgb: RGB image.
        Returns:
            str: Extracted text.
        """
        logger.info(f"Start to extracte the text information out of the image.")
        return pytesseract.image_to_string(image_rgb)

    async def process(self):
        """
        Asynchronous method to process the image and extract text.
        Returns:
            str: Extracted text from the image.
        """
        logger.info(f"Start the OCR reading for the image:{self.picture_file_path}")
        image_rgb = self.load_image(self.picture_file_path)[1]
        text = self.extract_text(image_rgb)
        logger.info(f"Successfully read the text information out of the image:{self.picture_file_path} with the OCR Feature.")
        return text
    
    def configure(self, picture_file_path: str):
        """
        Configures the OCR feature with a new image path.
        Args:
            picture_file_path (str): Path to the new image file.
        """
        logger.info(f"Configuration of the OCR feature.")
        self.picture_file_path = picture_file_path

async def main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(parent_dir, "Resources", "Images", "example3.png")

    ocr = OCRFeature()
    ocr.configure(image_path)

    text = await ocr.process()

    print("\n=== Extracted Text ===")
    print(text)

    _, image_rgb = ocr.load_image(image_path)
    plt.figure(figsize=(10, 6))
    plt.imshow(image_rgb)
    plt.title("Original Image")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())