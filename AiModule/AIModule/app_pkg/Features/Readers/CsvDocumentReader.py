import asyncio
import csv
import os

from .BaseDocumentReader import BaseDocumentReader


class CsvDocumentReader(BaseDocumentReader):
    """
    Reader implementation for CSV files.

    Reads CSV files as dictionaries using the first row as headers.
    """

    def __init__(self):
        """Initializes the CSV reader state."""
        super().__init__()
        self.rows: list[dict[str, str]] = []

    def _load_document(self) -> None:
        """
        Loads the CSV file into memory.
        """

        if not self.file_path:
            raise ValueError("CSV file path not configured.")

        with open(self.file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            self.rows = list(reader)

    def read_document(self) -> str:
        """
        Converts the CSV rows into readable plain text.
        """

        if not self.rows:
            return ""

        lines = []

        for row in self.rows:
            line = " | ".join(
                f"{key}: {value}"
                for key, value in row.items()
            )
            lines.append(line)

        return "\n".join(lines)

    def read_rows(self) -> list[dict[str, str]]:
        """
        Returns the CSV rows as dictionaries.
        """

        return self.rows

    def read_columns(self) -> list[str]:
        """
        Returns all CSV column names.
        """

        if not self.rows:
            return []

        return list(self.rows[0].keys())


async def main():
    """
    Tests the CsvDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "example.csv")

    reader = CsvDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")

    result = await reader.process()

    print("\n=== CSV DOCUMENT RESULT ===")
    print(result)

    print("\n=== CSV COLUMNS ===")
    print(reader.read_columns())

    print("\n=== CSV ROWS ===")
    print(reader.read_rows())


if __name__ == "__main__":
    asyncio.run(main())