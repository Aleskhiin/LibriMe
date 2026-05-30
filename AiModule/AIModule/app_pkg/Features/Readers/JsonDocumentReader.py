import asyncio
import json
import os
from typing import Any

from .BaseDocumentReader import BaseDocumentReader


class JsonDocumentReader(BaseDocumentReader):
    """
    Reader implementation for JSON files.
    """

    def __init__(self):
        """Initializes the JSON reader state."""
        super().__init__()
        self.data: Any = None

    def _load_document(self) -> None:
        """
        Loads and parses the JSON file.
        """

        if not self.file_path:
            raise ValueError("JSON file path not configured.")

        with open(self.file_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def read_document(self) -> str:
        """
        Returns the JSON content formatted as readable text.
        """

        if self.data is None:
            return ""

        return json.dumps(
            self.data,
            indent=2,
            ensure_ascii=False
        )

    def read_data(self) -> Any:
        """
        Returns the parsed JSON data.
        """

        return self.data

    def read_keys(self) -> list[str]:
        """
        Returns top-level keys if the JSON root is an object.
        """

        if isinstance(self.data, dict):
            return list(self.data.keys())

        return []


async def main():
    """
    Tests the JsonDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "example.json")

    reader = JsonDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")

    result = await reader.process()

    print("\n=== JSON DOCUMENT RESULT ===")
    print(result)

    print("\n=== JSON KEYS ===")
    print(reader.read_keys())

    print("\n=== JSON RAW DATA ===")
    print(reader.read_data())


if __name__ == "__main__":
    asyncio.run(main())