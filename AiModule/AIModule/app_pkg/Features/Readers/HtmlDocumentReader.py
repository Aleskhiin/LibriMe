import asyncio
import os

from bs4 import BeautifulSoup

from .BaseDocumentReader import BaseDocumentReader


class HtmlDocumentReader(BaseDocumentReader):
    """
    Reader implementation for HTML files.

    Extracts visible text, headings, and links.
    """

    def __init__(self):
        """Initializes the HTML reader state."""
        super().__init__()
        self.html_content: str = ""
        self.soup: BeautifulSoup | None = None

    def _load_document(self) -> None:
        """
        Loads and parses the HTML document.
        """

        if not self.file_path:
            raise ValueError("HTML file path not configured.")

        with open(self.file_path, "r", encoding="utf-8") as file:
            self.html_content = file.read()

        self.soup = BeautifulSoup(self.html_content, "html.parser")

    def read_document(self) -> str:
        """
        Returns the visible HTML text.
        """

        if not self.soup:
            raise RuntimeError("HTML document not loaded.")

        return self.soup.get_text(separator="\n", strip=True)

    def read_headings(self) -> list[str]:
        """
        Extracts all HTML headings.

        Returns:
            List of heading texts.
        """

        if not self.soup:
            raise RuntimeError("HTML document not loaded.")

        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        return [heading.get_text(strip=True) for heading in headings]

    def read_links(self) -> list[dict[str, str]]:
        """
        Extracts all HTML links.

        Returns:
            List of dictionaries with link text and URL.
        """

        if not self.soup:
            raise RuntimeError("HTML document not loaded.")

        links = []

        for link in self.soup.find_all("a"):
            text = link.get_text(strip=True)
            href = link.get("href")

            if href:
                links.append({
                    "text": text,
                    "url": href
                })

        return links


async def main():
    """
    Tests the HtmlDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "example.html")

    reader = HtmlDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")

    result = await reader.process()

    print("\n=== HTML DOCUMENT RESULT ===")
    print(result)

    print("\n=== HTML HEADINGS ===")
    print(reader.read_headings())

    print("\n=== HTML LINKS ===")
    print(reader.read_links())


if __name__ == "__main__":
    asyncio.run(main())