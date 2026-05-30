import asyncio
import os

from .BaseDocumentReader import BaseDocumentReader


class TextDocumentReader(BaseDocumentReader):
    """
    Reader implementation for plain text files.
    """

    def __init__(self):
        """Initializes the text reader state."""
        super().__init__()
        self.content: str = ""

    def _load_document(self) -> None:
        """
        Loads the text file into memory.
        """

        if not self.file_path:
            raise ValueError("Text file path not configured.")

        # Read the whole text file using UTF-8 encoding
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.content = file.read()

    def read_document(self) -> str:
        """
        Returns the complete text file content.
        """

        return self.content


async def main():
    """
    Tests the TextDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "example.txt")

    reader = TextDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")

    result = await reader.process()

    print("\n=== TEXT DOCUMENT RESULT ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())