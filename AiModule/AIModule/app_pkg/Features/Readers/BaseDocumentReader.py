from abc import abstractmethod
from typing import Any, List, Literal, Optional
import re

from ..BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger


ReaderMode = Literal["document", "pages", "paragraphs"]


class BaseDocumentReader(BaseFeature):
    """
    Abstract base class for all document readers.

    This class defines the common interface and shared workflow for
    reading documents in different modes.
    """

    def __init__(self):
        """Initializes the common reader configuration."""
        self.file_path: Optional[str] = None
        self.reader_mode: ReaderMode = "document"
        self.page_numbers: List[int] = []

    def configure(
        self,
        file_path: str,
        reader_mode: ReaderMode = "document",
        page_numbers: List[int] | None = None
    ) -> None:
        """
        Configures the document reader.

        Args:
            file_path: Path to the input document.
            reader_mode: Reading mode: document, pages, or paragraphs.
            page_numbers: Optional 0-based page or slide indexes.
        """

        self.file_path = file_path
        self.reader_mode = reader_mode
        self.page_numbers = page_numbers or []

        logger.info(
            f"Configured {self.__class__.__name__}. "
            f"mode={reader_mode}, pages={self.page_numbers}"
        )

    @abstractmethod
    def _load_document(self) -> None:
        """
        Loads the document into memory.

        Must be implemented by each concrete reader.
        """
        pass

    @abstractmethod
    def read_document(self) -> str:
        """
        Reads the complete document as text.

        Returns:
            Extracted document text.
        """
        pass

    def read_pages(self, page_numbers: List[int]) -> str:
        """
        Reads selected pages or slides.

        Args:
            page_numbers: 0-based page or slide indexes.

        Raises:
            NotImplementedError: If the reader does not support pages.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support page-based reading."
        )

    def read_paragraphs(self) -> List[str]:
        """
        Reads the document and splits it into paragraphs.

        Returns:
            List of extracted paragraphs.
        """

        text = self.read_document()
        return self._split_into_paragraphs(text)

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Splits text into paragraphs using simple formatting heuristics.

        Args:
            text: Input text.

        Returns:
            Clean list of paragraphs.
        """

        # Normalize all newline variants to Unix style
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Merge hyphenated line breaks, for example "soft-\nware"
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Merge wrapped lines when the next line starts with a lowercase letter
        text = re.sub(r"(?<!\n)\n([a-zäöüß])", r" \1", text)

        # Split paragraphs on empty lines
        raw_paragraphs = re.split(r"\n\s*\n", text)

        return [p.strip() for p in raw_paragraphs if p.strip()]

    async def process(self) -> Any:
        """
        Executes the reader workflow.

        Returns:
            Extracted document content depending on the selected reader mode.
        """

        # Load the document before reading content
        self._load_document()

        if self.reader_mode == "document":
            return self.read_document()

        if self.reader_mode == "pages":
            return self.read_pages(self.page_numbers)

        if self.reader_mode == "paragraphs":
            return self.read_paragraphs()

        raise ValueError(f"Unsupported reader mode: {self.reader_mode}")