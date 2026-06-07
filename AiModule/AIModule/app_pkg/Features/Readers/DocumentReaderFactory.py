import asyncio
import os
from pathlib import Path

from .BaseDocumentReader import BaseDocumentReader
from .PDFDocumentReader import PDFDocumentReader
from .TextDocumentReader import TextDocumentReader
from .MarkdownDocumentReader import MarkdownDocumentReader
from .WordDocumentReader import WordDocumentReader
from .ODTDocumentReader import ODTDocumentReader
from .PresentationDocumentReader import PresentationDocumentReader
from .HtmlDocumentReader import HtmlDocumentReader
from .CsvDocumentReader import CsvDocumentReader
from .JsonDocumentReader import JsonDocumentReader


class DocumentReaderFactory:
    """
    Factory class for creating document readers.

    The factory selects the correct reader implementation based on
    the file extension.
    """

    _readers = {
        ".pdf": PDFDocumentReader,

        ".txt": TextDocumentReader,

        ".md": MarkdownDocumentReader,
        ".markdown": MarkdownDocumentReader,

        ".doc": WordDocumentReader,
        ".docx": WordDocumentReader,
        ".odt": ODTDocumentReader,

        ".ppt": PresentationDocumentReader,
        ".pptx": PresentationDocumentReader,

        ".html": HtmlDocumentReader,
        ".htm": HtmlDocumentReader,

        ".csv": CsvDocumentReader,

        ".json": JsonDocumentReader,
    }

    @classmethod
    def create_reader(cls, file_path: str) -> BaseDocumentReader:
        """
        Creates the matching reader for a file.

        Args:
            file_path: Path to the input file.

        Returns:
            A concrete BaseDocumentReader implementation.

        Raises:
            ValueError: If the file extension is not supported.
        """

        suffix = Path(file_path).suffix.lower()

        reader_cls = cls._readers.get(suffix)

        if not reader_cls:
            raise ValueError(f"Unsupported file type: {suffix}")

        return reader_cls()

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """
        Returns all supported file extensions.
        """

        return list(cls._readers.keys())


async def main():
    """
    Tests the DocumentReaderFactory directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    testfiles_dir = os.path.join(base_dir, "Testfiles")

    test_files = [
        "Fuchs_HA8.pdf",
        "example.txt",
        "example.md",
        "example.docx",
        "example.doc",
        "example.odt",
        "example.pptx",
        "example.ppt",
        "example.html",
        "example.csv",
        "example.json",
    ]

    for file_name in test_files:
        file_path = os.path.join(testfiles_dir, file_name)

        if not os.path.exists(file_path):
            print(f"\nSkipping {file_name}: file does not exist.")
            continue

        try:
            reader = DocumentReaderFactory.create_reader(file_path)

            reader.configure(
                file_path=file_path,
                reader_mode="document"
            )

            result = await reader.process()

            print(f"\n=== FACTORY RESULT: {file_name} ===")
            print(f"Reader class: {reader.__class__.__name__}")
            print(result)

        except Exception as ex:
            print(f"\nFactory test failed for {file_name}: {ex}")


if __name__ == "__main__":
    asyncio.run(main())