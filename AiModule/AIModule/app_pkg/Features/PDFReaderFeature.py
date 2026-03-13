import asyncio
import io
import os
from typing import List, Literal, Optional

import PyPDF2
from .BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger
import re


class PDFReaderFeature(BaseFeature):
    def __init__(self):
        self.reader: Optional[PyPDF2.PdfReader] = None
        self.pdf_file_path: Optional[str] = None
        self.reader_mode: Optional[Literal["document", "pages", "paragraphs"]] = None
        self.page_numbers: List[int] = []
        self._pdf_stream: Optional[io.BytesIO] = None  # keep ref to ensure stream lifetime

    def _load_pdf(self):
        """Load the PDF file into memory using BytesIO."""
        if not self.pdf_file_path:
            logger.error("PDF file path not configured.")
            raise ValueError("PDF file path not configured.")

        try:
            logger.info(f"Trying to load PDF: {self.pdf_file_path}")
            with open(self.pdf_file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            self._pdf_stream = io.BytesIO(pdf_data)
            self.reader = PyPDF2.PdfReader(self._pdf_stream)

            # If encrypted, try decrypting with empty password (common case)
            if getattr(self.reader, "is_encrypted", False):
                try:
                    self.reader.decrypt("")
                    logger.info("PDF was encrypted; attempted empty-password decryption.")
                except Exception as de:
                    logger.warning(f"Encrypted PDF could not be decrypted: {de}")

            logger.info(f"Successfully loaded PDF: {self.pdf_file_path}")

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise RuntimeError(f"Error loading PDF: {e}")

    def _extract_page_text(self, page_index: int) -> str:
        """Extract text from a single page; guard against None and normalize newlines."""
        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        if not (0 <= page_index < len(self.reader.pages)):
            raise IndexError(f"Page {page_index} out of range.")

        try:
            raw = self.reader.pages[page_index].extract_text()
            text = raw or ""  # PyPDF2 may return None
            # Normalize Windows/Mac newlines to '\n'
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            return text
        except Exception as e:
            logger.warning(f"Failed to extract text from page {page_index}: {e}")
            return ""

    def read_document(self) -> str:
        """Read the entire PDF document and return its text with page markers."""
        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        logger.info("Extracting text for the entire document.")
        parts = []
        for i in range(len(self.reader.pages)):
            page_text = self._extract_page_text(i)
            # Add a visible page separator to preserve structure
            parts.append(f"=== [Seite {i}] ===\n{page_text.strip()}")
        return "\n\n".join(parts)

    def read_pages(self, page_numbers: List[int]) -> str:
        """Read specific pages from the PDF; page_numbers are 0-based."""
        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        logger.info(f"Extracting text for pages: {page_numbers}")
        valid_pages = []
        for num in page_numbers:
            if 0 <= num < len(self.reader.pages):
                page_text = self._extract_page_text(num).strip()
                valid_pages.append(f"=== [Seite {num}] ===\n{page_text}")
            else:
                logger.warning(f"Page {num} is out of range. Skipping.")

        if not valid_pages:
            raise ValueError("No valid pages to read.")

        return "\n\n".join(valid_pages)

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs robustly:
        - split on 2+ newlines (allowing spaces)
        - keep bullet lists together if possible
        - trim whitespace
        """
        # Normalize newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Heuristic: merge hyphenated line breaks (e.g., 'Agili-\n tät' -> 'Agilität')
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Heuristic: merge line-wrapped sentences where the next line starts lowercase
        text = re.sub(r"(?<!\n)\n([a-zäöüß])", r" \1", text)

        # Split on 2+ newlines (optionally with spaces)
        raw_paragraphs = re.split(r"\n\s*\n", text)

        # Clean up paragraphs
        paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]

        return paragraphs

    def read_paragraphs(
        self,
        mode: Literal["all", "pages"],
        page_numbers: List[int] = None
    ) -> List[str]:
        """
        Read paragraphs from the whole document or specific pages.
        For 'pages', page_numbers must be provided (0-based indexes).
        """
        if not self.reader:
            raise RuntimeError("PDF not loaded.")

        if mode == "all":
            logger.info("Extracting paragraphs for the entire document.")
            text = self.read_document()
        elif mode == "pages":
            if not page_numbers:
                logger.error("Missing page_numbers for 'pages' mode.")
                raise ValueError("Missing page_numbers for 'pages' mode.")
            logger.info(f"Extracting paragraphs for pages: {page_numbers}")
            text = self.read_pages(page_numbers)
        else:
            logger.error("Invalid mode for read_paragraphs().")
            raise ValueError("Invalid mode for read_paragraphs().")

        paragraphs = self._split_into_paragraphs(text)
        logger.info(f"Split into {len(paragraphs)} paragraphs.")
        return paragraphs

    async def process(self):
        """Process the PDF based on the selected mode."""
        logger.info("Starting PDF extraction (process).")
        self._load_pdf()

        if self.reader_mode == "document":
            return self.read_document()
        elif self.reader_mode == "pages":
            return self.read_pages(self.page_numbers)
        elif self.reader_mode == "paragraphs":
            # Default to 'pages' if page_numbers given; else all
            if self.page_numbers:
                return self.read_paragraphs(mode="pages", page_numbers=self.page_numbers)
            else:
                return self.read_paragraphs(mode="all")
        else:
            logger.warning("Unknown reader_mode; defaulting to document.")
            return self.read_document()

    def configure(
        self,
        pdf_file_path: str,
        reader_mode: Literal["document", "pages", "paragraphs"],
        page_numbers: List[int] = None
    ):
        """Configure the PDF reader."""
        self.pdf_file_path = pdf_file_path
        self.reader_mode = reader_mode
        self.page_numbers = page_numbers or []
        logger.info(f"Configured PDFReaderFeature. mode={reader_mode}, pages={self.page_numbers}")


# --- Example usage / manual test ---
async def main():
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Testfiles")
    )
    file_path = os.path.join(base_path, "Fuchs_HA8.pdf")

    print("=== Test: Entire Document ===")
    feature_document = PDFReaderFeature()
    feature_document.configure(pdf_file_path=file_path, reader_mode="document")
    document_text = await feature_document.process()
    print(document_text)

    print("\n=== Test: Pages 0 and 1 ===")
    feature_pages = PDFReaderFeature()
    feature_pages.configure(pdf_file_path=file_path, reader_mode="pages", page_numbers=[0, 1])
    pages_text = await feature_pages.process()
    print(pages_text)

    print("\n=== Test: Paragraphs from Page 0 ===")
    feature_paragraphs = PDFReaderFeature()
    feature_paragraphs.configure(pdf_file_path=file_path, reader_mode="paragraphs", page_numbers=[0])
    paragraphs_text = await feature_paragraphs.process()
    for i, paragraph in enumerate(paragraphs_text, start=1):
        print(f"Paragraph {i}: {paragraph}")


if __name__ == "__main__":
    asyncio.run(main())