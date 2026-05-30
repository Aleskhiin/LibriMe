import asyncio
import os
import re

from .TextDocumentReader import TextDocumentReader


class MarkdownDocumentReader(TextDocumentReader):
    """
    Reader implementation for Markdown files.

    Markdown is read as plain text, but this class also provides
    helper methods for headings, links, images, and code blocks.
    """

    def read_headings(self) -> list[str]:
        """
        Extracts all Markdown headings.

        Returns:
            List of heading texts without leading # characters.
        """

        return re.findall(r"^#{1,6}\s+(.+)$", self.content, re.MULTILINE)

    def read_links(self) -> list[dict[str, str]]:
        """
        Extracts Markdown links.

        Returns:
            List of dictionaries with link text and URL.
        """

        matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", self.content)

        return [
            {"text": text, "url": url}
            for text, url in matches
        ]

    def read_images(self) -> list[dict[str, str]]:
        """
        Extracts Markdown images.

        Returns:
            List of dictionaries with alt text and image URL.
        """

        matches = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", self.content)

        return [
            {"alt": alt, "url": url}
            for alt, url in matches
        ]

    def read_code_blocks(self) -> list[str]:
        """
        Extracts fenced Markdown code blocks.

        Returns:
            List of code block contents.
        """

        return re.findall(
            r"```(?:\w+)?\n(.*?)```",
            self.content,
            re.DOTALL
        )

    def read_document_without_markdown(self) -> str:
        """
        Removes common Markdown syntax and returns cleaned text.

        Returns:
            Markdown content converted to a simpler plain-text form.
        """

        text = self.content

        # Remove fenced code blocks
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        # Remove images
        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", "", text)

        # Replace links with their visible text
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

        # Remove heading markers
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

        # Remove common inline Markdown characters
        text = re.sub(r"[*_`>#-]", "", text)

        return text.strip()


async def main():
    """
    Tests the MarkdownDocumentReader directly.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "Testfiles", "example.md")

    reader = MarkdownDocumentReader()
    reader.configure(file_path=file_path, reader_mode="document")

    result = await reader.process()

    print("\n=== MARKDOWN DOCUMENT RESULT ===")
    print(result)

    print("\n=== MARKDOWN HEADINGS ===")
    print(reader.read_headings())

    print("\n=== MARKDOWN LINKS ===")
    print(reader.read_links())

    print("\n=== MARKDOWN IMAGES ===")
    print(reader.read_images())

    print("\n=== MARKDOWN CODE BLOCKS ===")
    print(reader.read_code_blocks())

    print("\n=== MARKDOWN WITHOUT MARKDOWN SYNTAX ===")
    print(reader.read_document_without_markdown())


if __name__ == "__main__":
    asyncio.run(main())