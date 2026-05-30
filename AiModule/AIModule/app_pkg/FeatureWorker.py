import asyncio
import os
from typing import List, Dict, Any

from app_pkg.Features.OCRFeature import OCRFeature
from app_pkg.Features.Readers.DocumentReaderFactory import DocumentReaderFactory
from app_pkg.Features.TextToSpeechFeature import TextToSpeechFeature
from app_pkg.Features.TranslatorFeature import TranslatorFeature
from app_pkg.Logger.Logging_setup import logger


class FeatureWorker:
    """
    Coordinates the complete processing workflow.

    Depending on the input file type, this worker:
    - extracts text from images via OCR
    - extracts text from documents via DocumentReaderFactory
    - optionally translates the extracted text
    - generates speech audio from the final text
    """

    def __init__(
        self,
        tts_output_dir: str = "./output",
        from_lang: str = "de",
        to_lang: str = "en"
    ):
        """
        Initializes all required feature modules once.

        Args:
            tts_output_dir: Directory where generated audio files are stored.
            from_lang: Source language for optional translation.
            to_lang: Target language for optional translation and TTS.
        """

        # Text-to-speech feature for audio generation
        self.tts = TextToSpeechFeature(output_dir=tts_output_dir)

        # OCR feature for image-based text extraction
        self.ocr = OCRFeature()

        # Translator feature for optional language translation
        self.translator = TranslatorFeature()

        # Language configuration
        self.from_lang = from_lang
        self.to_lang = to_lang

    async def run(
        self,
        input_file: str,
        ref_audio: str = None,
        filename: str = "result",
        read_mode: str = "document",
        page_numbers: List[int] | None = None
    ) -> Dict[str, Any]:
        """
        Runs the complete workflow for a given input file.

        Supported inputs:
        - Images: .png, .jpg, .jpeg
        - Documents: .pdf, .txt, .md, .doc, .docx, .odt, .ppt, .pptx,
          .html, .csv, .json

        Args:
            input_file: Path to the input file.
            ref_audio: Optional reference audio path. Currently not used here,
                but kept for compatibility with previous calls.
            filename: Base filename for generated audio output.
            read_mode: Defines how documents should be read:
                - "document": whole document as one text
                - "pages": page-/slide-based chunks, if supported
                - "paragraphs": paragraph-based chunks
            page_numbers: Optional list of 0-based page or slide indexes.

        Returns:
            Dictionary containing extracted text and generated audio path(s).
        """

        # Extract file extension and normalize it
        ext = os.path.splitext(input_file)[1].lower()

        # Image files are handled via OCR
        if ext in [".png", ".jpg", ".jpeg"]:
            return await self._process_image(
                input_file=input_file,
                filename=filename
            )

        # All supported document formats are handled via DocumentReaderFactory
        supported_document_types = {
            ".pdf",
            ".txt",
            ".md",
            ".markdown",
            ".doc",
            ".docx",
            ".odt",
            ".ppt",
            ".pptx",
            ".html",
            ".htm",
            ".csv",
            ".json",
        }

        if ext in supported_document_types:
            return await self._process_document(
                input_file=input_file,
                filename=filename,
                read_mode=read_mode,
                page_numbers=page_numbers
            )

        # If the file type is unknown, fail explicitly
        logger.error(f"Unsupported file type: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")

    async def _process_image(
        self,
        input_file: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Processes image files.

        The image workflow is:
        image -> OCR -> optional translation -> TTS -> audio file

        Args:
            input_file: Path to the image file.
            filename: Base filename for the generated audio file.

        Returns:
            Dictionary with extracted text and generated audio path.
        """

        logger.info("Start extracting text out of the image.")

        # Configure OCR with the selected image path
        self.ocr.configure(picture_file_path=input_file)

        # OCRFeature.process() is asynchronous
        text: str = await self.ocr.process()

        logger.info("Finish extracting text out of the image.")

        # Translate only if source and target language differ
        text = self._maybe_translate(text)

        # Generate one audio file for the complete OCR result
        audio_path = self._tts_single(
            text=text,
            filename=filename
        )

        return {
            "text": text,
            "audio": audio_path
        }

    async def _process_document(
        self,
        input_file: str,
        filename: str,
        read_mode: str,
        page_numbers: List[int] | None = None
    ) -> Dict[str, Any]:
        """
        Processes document files through the generic reader system.

        The document workflow is:
        document -> DocumentReaderFactory -> optional translation -> TTS

        Args:
            input_file: Path to the document file.
            filename: Base filename for generated audio files.
            read_mode: Reading mode for the document.
            page_numbers: Optional list of 0-based page/slide indexes.

        Returns:
            Dictionary with either:
            - one text and one audio file for "document" mode
            - multiple text chunks and audio files for chunked modes
        """

        # Validate read mode and fallback to document mode if invalid
        mode = read_mode if read_mode in {
            "document",
            "pages",
            "paragraphs"
        } else "document"

        logger.info(
            f"Start extracting text out of document "
            f"'{input_file}' with read_mode='{mode}'."
        )

        # Create the correct reader based on the file extension
        reader = DocumentReaderFactory.create_reader(input_file)

        # Configure the selected reader.
        # page_numbers are used by readers that support page/slide selection.
        reader.configure(
            file_path=input_file,
            reader_mode=mode,
            page_numbers=page_numbers
        )

        # Execute the reader asynchronously via BaseFeature interface
        result = await reader.process()

        logger.info("Finish extracting text out of document.")

        # In document mode, all content becomes one audio file
        if mode == "document":
            text = self._normalize_to_text(result)

            # Optional translation of the complete document text
            text = self._maybe_translate(text)

            # Generate one audio file
            audio_path = self._tts_single(
                text=text,
                filename=filename
            )

            return {
                "text": text,
                "audio": audio_path
            }

        # In pages/paragraphs mode, content is handled as chunks
        chunks = self._normalize_to_chunks(result)

        if not chunks:
            raise ValueError(
                "Document reader returned no content for the selected read_mode."
            )

        # Translate each chunk separately if needed
        if self.from_lang != self.to_lang:
            logger.info(
                f"Start translation per chunk from "
                f"{self.from_lang} to {self.to_lang}."
            )

            translated_chunks: List[str] = []

            for chunk in chunks:
                self.translator.configure(
                    self.from_lang,
                    self.to_lang,
                    chunk
                )

                translated_chunks.append(self.translator.process())

            chunks = translated_chunks

            logger.info("Finish translation per chunk.")

        # Generate one audio file per chunk
        audio_files: List[str] = []

        for i, chunk in enumerate(chunks, start=1):
            suffix = self._build_chunk_suffix(mode, i)

            audio_files.append(
                self._tts_single(
                    text=chunk,
                    filename=f"{filename}{suffix}"
                )
            )

        return {
            "texts": chunks,
            "audios": audio_files
        }

    def _normalize_to_text(self, result) -> str:
        """
        Converts a reader result into a single text string.

        Some readers may return a list in special cases.
        This method defensively joins list values into one text.
        """

        if isinstance(result, list):
            return "\n\n".join(
                str(item)
                for item in result
                if str(item).strip()
            )

        return str(result or "")

    def _normalize_to_chunks(self, result) -> List[str]:
        """
        Converts a reader result into a clean list of text chunks.

        Used for page-based, slide-based, or paragraph-based processing.
        """

        if isinstance(result, list):
            return [
                str(item).strip()
                for item in result
                if str(item).strip()
            ]

        text = str(result or "").strip()

        if not text:
            return []

        return [text]

    def _build_chunk_suffix(self, mode: str, index: int) -> str:
        """
        Creates deterministic filename suffixes for generated audio chunks.

        Examples:
        - pages mode: _p1, _p2, ...
        - paragraphs mode: _seg1, _seg2, ...
        """

        if mode == "pages":
            return f"_p{index}"

        if mode == "paragraphs":
            return f"_seg{index}"

        return f"_part{index}"

    def _maybe_translate(self, text: str) -> str:
        """
        Translates text only when source and target languages differ.
        """

        if self.from_lang != self.to_lang:
            logger.info(
                f"Start translation of the text from "
                f"{self.from_lang} to {self.to_lang}."
            )

            self.translator.configure(
                self.from_lang,
                self.to_lang,
                text
            )

            text = self.translator.process()

            logger.info("Finish translation of the text.")

        return text

    def _tts_single(self, text: str, filename: str) -> str:
        """
        Generates exactly one audio file for a given text.
        """

        logger.info("Start to configure audio generation module.")

        self.tts.configure(
            gen_text=text,
            filename=filename,
            output_dir=self.tts.output_dir,
            language=self.to_lang
        )

        logger.info("Finish to configure audio generation module.")
        logger.info("Start to generate the audio file.")

        audio_path = self.tts.process()

        logger.info("Successfully generated the audio file.")

        return audio_path
    
# -------------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------------

async def main():
    """
    Demonstrates the usage of FeatureWorker with all supported file types.

    The examples cover:
    - Image OCR processing
    - PDF document processing
    - PDF page-based processing
    - PDF paragraph-based processing
    - Word documents (.docx/.doc)
    - OpenDocument files (.odt)
    - Presentations (.pptx/.ppt)
    - Markdown files
    - HTML files
    - CSV files
    - JSON files
    """

    parent_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    resources_dir = os.path.join(
        parent_dir,
        "app_pkg",
        "Resources"
    )

    testfiles_dir = os.path.join(
        parent_dir,
        "app_pkg",
        "Testfiles"
    )

    image_path = os.path.join(
        resources_dir,
        "Images",
        "lord_of _the _ring.png"
    )

    ref_audio = os.path.join(
        resources_dir,
        "Audio",
        "unbenannt.wav"
    )

    worker = FeatureWorker(
        tts_output_dir="./tts_output",
        from_lang="en",
        to_lang="de"
    )

    # ------------------------------------------------------------------
    # Image -> OCR -> Translation -> TTS
    # ------------------------------------------------------------------

    try:
        result_img = await worker.run(
            input_file=image_path,
            ref_audio=ref_audio,
            filename="from_image",
            read_mode="document"
        )

        print("\n=== IMAGE RESULT ===")
        print(result_img)

    except Exception as ex:
        print(f"Image test failed: {ex}")

    # ------------------------------------------------------------------
    # Test all supported document formats
    # ------------------------------------------------------------------

    test_documents = [

        # PDF
        (
            "PDF Document",
            os.path.join(testfiles_dir, "Fuchs_HA8.pdf"),
            "pdf_document",
            "document"
        ),

        (
            "PDF Pages",
            os.path.join(testfiles_dir, "Fuchs_HA8.pdf"),
            "pdf_pages",
            "pages"
        ),

        (
            "PDF Paragraphs",
            os.path.join(testfiles_dir, "Fuchs_HA8.pdf"),
            "pdf_paragraphs",
            "paragraphs"
        ),

        # Word
        (
            "DOCX Document",
            os.path.join(testfiles_dir, "example.docx"),
            "docx_document",
            "document"
        ),

        (
            "DOC Document",
            os.path.join(testfiles_dir, "example.doc"),
            "doc_document",
            "document"
        ),

        # OpenDocument
        (
            "ODT Document",
            os.path.join(testfiles_dir, "example.odt"),
            "odt_document",
            "document"
        ),

        # Presentations
        (
            "PPTX Presentation",
            os.path.join(testfiles_dir, "example.pptx"),
            "pptx_document",
            "document"
        ),

        (
            "PPT Presentation",
            os.path.join(testfiles_dir, "example.ppt"),
            "ppt_document",
            "document"
        ),

        # Markdown
        (
            "Markdown Document",
            os.path.join(testfiles_dir, "example.md"),
            "markdown_document",
            "document"
        ),

        # HTML
        (
            "HTML Document",
            os.path.join(testfiles_dir, "example.html"),
            "html_document",
            "document"
        ),

        # CSV
        (
            "CSV Document",
            os.path.join(testfiles_dir, "example.csv"),
            "csv_document",
            "document"
        ),

        # JSON
        (
            "JSON Document",
            os.path.join(testfiles_dir, "example.json"),
            "json_document",
            "document"
        ),
    ]

    # ------------------------------------------------------------------
    # Execute all document tests
    # ------------------------------------------------------------------

    for (
        description,
        file_path,
        output_name,
        read_mode
    ) in test_documents:

        if not os.path.exists(file_path):
            print(
                f"\nSkipping {description}: "
                f"file does not exist ({file_path})"
            )
            continue

        try:
            result = await worker.run(
                input_file=file_path,
                ref_audio=ref_audio,
                filename=output_name,
                read_mode=read_mode
            )

            print(f"\n=== {description.upper()} ===")
            print(result)

        except Exception as ex:
            print(
                f"\n{description} test failed:"
                f"\n{ex}"
            )


# -------------------------------------------------------------------------
# Application entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())