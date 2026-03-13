import PyPDF2
from typing import List, Literal
import os
import io


class PDFReader:
    """
    A class for reading PDF files with flexible options:
    - Read the entire document
    - Read specific pages
    - Read paragraphs (based on line breaks)
    """

    def __init__(self, file_path: str):
        """
        Initialize the PDFReader with the path to the PDF file.
        :param file_path: Path to the PDF file.
        """
        self.file_path = file_path
        self.reader = None
        self._load_pdf()

    def _load_pdf(self):
        """Load the PDF file into memory using BytesIO."""
        try:
            with open(self.file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            # Wrap bytes in BytesIO so PdfReader can seek
            pdf_stream = io.BytesIO(pdf_data)
            self.reader = PyPDF2.PdfReader(pdf_stream)
        except Exception as e:
            raise RuntimeError(f"Error loading PDF: {e}")

    def read_document(self) -> str:
        """Read the entire PDF document and return its text."""
        return "\n".join(page.extract_text() or "" for page in self.reader.pages)

    def read_pages(self, page_numbers: List[int]) -> str:
        """Read specific pages from the PDF."""
        text = ""
        for num in page_numbers:
            if 0 <= num < len(self.reader.pages):
                text += self.reader.pages[num].extract_text() + "\n"
            else:
                print(f"Page {num} does not exist.")
        return text

    def read_paragraphs(self, mode: Literal["all", "pages"], page_numbers: List[int] = None) -> List[str]:
        """Read paragraphs from the document or specific pages."""
        text = ""
        if mode == "all":
            text = self.read_document()
        elif mode == "pages" and page_numbers:
            text = self.read_pages(page_numbers)
        else:
            raise ValueError("Invalid mode or missing page numbers.")

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return paragraphs





# Example usage:
if __name__ == "__main__":
    
    base_path = os.path.dirname(__file__)  # directory of the script
    file_path = os.path.join(base_path, "documents", "Fuchs_HA8.pdf")
    pdf_reader = PDFReader(file_path)

    print("=== Entire Document ===")
    print(pdf_reader.read_document())

    print("\n=== Pages 0 and 1 ===")
    print(pdf_reader.read_pages([0, 1]))

    print("\n=== Paragraphs from Page 0 ===")
    paragraphs = pdf_reader.read_paragraphs(mode="pages", page_numbers=[0])
    for i, p in enumerate(paragraphs, start=1):
        print(f"Paragraph {i}: {p}")