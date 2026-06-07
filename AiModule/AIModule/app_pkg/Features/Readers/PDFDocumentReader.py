import asyncio
import io
import os
from typing import List, Optional

import PyPDF2

from .BaseDocumentReader import BaseDocumentReader
from app_pkg.Logger.Logging_setup import logger


class PDFDocumentReader(BaseDocumentReader):
    """
    Reader implementation for PDF files.

    Supports:
    - complete document reading
    - selected page reading
    - paragraph extraction through BaseDocumentReader
    """

    def __init__(self):
        """Initializes the PDF reader state."""
        super().__init__()
        self.reader: Optional[PyPDF2.PdfReader] = None
        self._pdf_stream: Optional[io.BytesIO] = None

    def _load_document(self) -> None:
        """
        Loads the PDF file into memory.

        The BytesIO stream is stored as an instance attribute to keep
        the underlying stream alive while PyPDF2 reads the document.
        """

        if not self.file_path:
            raise ValueError("PDF file path not configured.")

        try:
            logger.info(f"Trying to load PDF: {self.file_path}")

            # Read the complete PDF file into memory
            with open(self.file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            # Keep a reference to the stream so PyPDF2 can access it safely
            self._pdf_stream = io.BytesIO(pdf_data)
            self.reader = PyPDF2.PdfReader(self._pdf_stream)

            # Try empty-password decryption for encrypted PDFs
            if getattr(self.reader, "is_encrypted", False):
                try:
                    self.reader.decrypt("")
                    logger.info("PDF was encrypted; attempted empty-password decryption.")
                except Exception as de:
                    logger.warning(f"Encrypted PDF could not be decrypted: {de}")

            logger.info(f"Successfully loaded PDF: {self.file_path}")

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise RuntimeError(f"Error loading PDF: {e}")

    def _extract_page_text(self, page_index: int) -> str:
        """
        Extracts text from a single PDF page.

        Args:
            page_index: 0-based page index.

        Returns:
            Extracted page text.
        """

        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        if not (0 <= page_index < len(self.reader.pages)):
            raise IndexError(f"Page {page_index} out of range.")

        try:
            raw = self.reader.pages[page_index].extract_text()
            text = raw or ""

            # Normalize newline characters
            return text.replace("\r\n", "\n").replace("\r", "\n")

        except Exception as e:
            logger.warning(f"Failed to extract text from page {page_index}: {e}")
            return ""

    def read_document(self) -> str:
        """
        Reads the complete PDF document.

        Returns:
            Extracted text with page markers.
        """

        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        parts = []

        for i in range(len(self.reader.pages)):
            page_text = self._extract_page_text(i)
            parts.append(f"=== [Page {i}] ===\n{page_text.strip()}")

        return "\n\n".join(parts)

    def read_pages(self, page_numbers: List[int]) -> str:
        """
        Reads selected PDF pages.

        Args:
            page_numbers: 0-based page indexes.

        Returns:
            Extracted text from the selected pages.
        """

        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        valid_pages = []

        for num in page_numbers:
            if 0 <= num < len(self.reader.pages):
                page_text = self._extract_page_text(num).strip()
                valid_pages.append(f"=== [Page {num}] ===\n{page_text}")
            else:
                logger.warning(f"Page {num} is out of range. Skipping.")

        if not valid_pages:
            raise ValueError("No valid pages to read.")

        return "\n\n".join(valid_pages)


async def main():
    """
    Tests the PDFDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "Fuchs_HA8.pdf")

    reader = PDFDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")
    print(await reader.process())

    reader = PDFDocumentReader()
    reader.configure(file_path=file_path, reader_mode="pages", page_numbers=[0, 1])
    print(await reader.process())

    reader = PDFDocumentReader()
    reader.configure(file_path=file_path, reader_mode="paragraphs")
    print(await reader.process())


if __name__ == "__main__":
    asyncio.run(main())