import asyncio
import os
import queue
from typing import List, Dict, Any

from app_pkg.Features.Images.ImageReaderFactory import ImageReaderFactory
from app_pkg.Features.Readers.DocumentReaderFactory import DocumentReaderFactory
from app_pkg.Features.TextToSpeechFeature import TextToSpeechFeature
from app_pkg.Features.TranslatorFeature import TranslatorFeature
from app_pkg.FeatureWorkerThread import FeatureWorkerThread
from app_pkg.Logger.Logging_setup import logger


class FeatureWorker:
    """
    Coordinates the complete processing workflow.

    Depending on the input file type, this worker:
    - extracts text from images via ImageReaderFactory
    - extracts text from documents via DocumentReaderFactory
    - optionally translates the extracted text
    - generates speech audio from the final text

    In addition, this class can optionally process tasks in background
    threads using a task queue.
    """

    def __init__(
        self,
        tts_output_dir: str = "./output",
        from_lang: str = "de",
        to_lang: str = "en",
        thread_count: int = 0
    ):
        """
        Initializes all required feature modules once.

        Args:
            tts_output_dir: Directory where generated audio files are stored.
            from_lang: Source language for optional translation.
            to_lang: Target language for optional translation and TTS.
            thread_count: Number of background worker threads.
                If 0, no background threads are started automatically.
        """

        # Text-to-speech feature for audio generation
        self.tts = TextToSpeechFeature(output_dir=tts_output_dir)

        # Translator feature for optional language translation
        self.translator = TranslatorFeature()

        # Language configuration
        self.from_lang = from_lang
        self.to_lang = to_lang

        # Queue support for optional background processing
        self.task_queue: queue.Queue = queue.Queue()
        self.threads: List[FeatureWorkerThread] = []
        self.thread_count = thread_count

    # ------------------------------------------------------------------
    # Queue / thread handling
    # ------------------------------------------------------------------

    def start_threads(self) -> None:
        """
        Starts all configured background worker threads.

        This method is only needed if tasks should be processed through
        the internal queue.
        """

        if self.thread_count <= 0:
            logger.info("No background worker threads configured.")
            return

        if self.threads:
            logger.warning("Background worker threads are already running.")
            return

        for worker_id in range(1, self.thread_count + 1):
            thread = FeatureWorkerThread(
                task_queue=self.task_queue,
                worker_id=worker_id
            )

            thread.start()
            self.threads.append(thread)

            logger.info(f"Started FeatureWorkerThread with id={worker_id}.")

    def enqueue(
        self,
        input_file: str,
        ref_audio: str = None,
        filename: str = "result",
        read_mode: str = "document",
        page_numbers: List[int] | None = None
    ) -> None:
        """
        Adds a file-processing task to the queue.

        Args:
            input_file: Path to the input file.
            ref_audio: Optional reference audio path. Currently kept for compatibility.
            filename: Base filename for generated audio output.
            read_mode: Document reading mode.
            page_numbers: Optional page or slide indexes.
        """

        self.task_queue.put((
            self.run,
            (),
            {
                "input_file": input_file,
                "ref_audio": ref_audio,
                "filename": filename,
                "read_mode": read_mode,
                "page_numbers": page_numbers
            }
        ))

        logger.info(f"Queued processing task for file: {input_file}")

    def wait_until_done(self) -> None:
        """
        Blocks until all queued tasks are completed.
        """

        self.task_queue.join()

    def stop_threads(self) -> None:
        """
        Stops all background worker threads.

        Threads stop after their current task or after their queue timeout.
        """

        for thread in self.threads:
            thread.stop()

        for thread in self.threads:
            thread.join(timeout=2)

        self.threads.clear()

        logger.info("Stopped all background worker threads.")

    # ------------------------------------------------------------------
    # Main processing workflow
    # ------------------------------------------------------------------

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
        - Images: all extensions supported by ImageReaderFactory
        - Documents: all extensions supported by DocumentReaderFactory

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

        # Image files are handled via ImageReaderFactory
        if ext in ImageReaderFactory.supported_extensions():
            return await self._process_image(
                input_file=input_file,
                filename=filename
            )

        # Document files are handled via DocumentReaderFactory
        if ext in DocumentReaderFactory.supported_extensions():
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
        image -> ImageReaderFactory -> OCRImageReader -> optional translation -> TTS

        Args:
            input_file: Path to the image file.
            filename: Base filename for the generated audio file.

        Returns:
            Dictionary with extracted text and generated audio path.
        """

        logger.info("Start extracting text out of the image.")

        # Create the correct image reader based on the file extension.
        reader = ImageReaderFactory.create_reader(input_file)

        # Configure the image reader with the selected image path.
        reader.configure(
            file_path=input_file
        )

        # Execute image reader processing asynchronously.
        text: str = await reader.process()

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

        reader = DocumentReaderFactory.create_reader(input_file)

        reader.configure(
            file_path=input_file,
            reader_mode=mode,
            page_numbers=page_numbers
        )

        try:
            result = await reader.process()

        except ValueError as e:
            logger.warning(
                f"Document reader returned no valid content: {e}. "
                f"Using fallback text."
            )
            result = "Datei leer"
            mode = "document"

        except Exception as e:
            logger.error(
                f"Unexpected document processing error: {e}. "
                f"Using fallback text.",
                exc_info=True
            )
            result = "Datei leer"
            mode = "document"

        logger.info("Finish extracting text out of document.")

        if mode == "document":
            text = self._normalize_to_text(result)

            if not text or not text.strip():
                logger.warning(
                    "Document contains no readable content. "
                    "Using fallback text."
                )
                text = "Datei leer"

            text = self._maybe_translate(text)

            audio_path = self._tts_single(
                text=text,
                filename=filename
            )

            return {
                "text": text,
                "audio": audio_path
            }

        chunks = self._normalize_to_chunks(result)

        if not chunks:
            logger.warning(
                "Document reader returned no chunks. "
                "Using fallback text."
            )
            chunks = ["Datei leer"]

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

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

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
    Demonstrates direct and queued usage of FeatureWorker.

    This test covers:
    - all supported image formats through ImageReaderFactory
    - all supported document formats through DocumentReaderFactory
    - direct async processing
    - queued background processing with FeatureWorkerThread
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

    image_dir = os.path.join(
        resources_dir,
        "Images"
    )

    testfiles_dir = os.path.join(
        parent_dir,
        "app_pkg",
        "Testfiles"
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
    # Test all supported image formats
    # ------------------------------------------------------------------

    test_images = [
        "example.png",
        "example.jpg",
        "example.jpeg",
        "example.bmp",
        "example.tif",
        "example.tiff",
        "example.webp",
        "lord_of _the _ring.png",
    ]

    for image_file in test_images:
        image_path = os.path.join(
            image_dir,
            image_file
        )

        if not os.path.exists(image_path):
            print(
                f"\nSkipping image: "
                f"file does not exist ({image_path})"
            )
            continue

        try:
            result = await worker.run(
                input_file=image_path,
                ref_audio=ref_audio,
                filename=f"image_{os.path.splitext(image_file)[0]}",
                read_mode="document"
            )

            print(f"\n=== IMAGE RESULT: {image_file.upper()} ===")
            print(result)

        except Exception as ex:
            print(
                f"\nImage test failed for {image_file}:"
                f"\n{ex}"
            )

    # ------------------------------------------------------------------
    # Test all supported document formats
    # ------------------------------------------------------------------

    test_documents = [
        (
            "PDF Document",
            "Fuchs_HA8.pdf",
            "pdf_document",
            "document",
            None
        ),
        (
            "PDF Pages",
            "Fuchs_HA8.pdf",
            "pdf_pages",
            "pages",
            [0, 1]
        ),
        (
            "PDF Paragraphs",
            "Fuchs_HA8.pdf",
            "pdf_paragraphs",
            "paragraphs",
            None
        ),
        (
            "TXT Document",
            "example.txt",
            "txt_document",
            "document",
            None
        ),
        (
            "Markdown Document",
            "example.md",
            "markdown_document",
            "document",
            None
        ),
        (
            "DOCX Document",
            "example.docx",
            "docx_document",
            "document",
            None
        ),
        (
            "DOC Document",
            "example.doc",
            "doc_document",
            "document",
            None
        ),
        (
            "ODT Document",
            "example.odt",
            "odt_document",
            "document",
            None
        ),
        (
            "PPTX Presentation",
            "example.pptx",
            "pptx_document",
            "document",
            None
        ),
        (
            "PPTX Slides",
            "example.pptx",
            "pptx_pages",
            "pages",
            [0, 1]
        ),
        (
            "PPT Presentation",
            "example.ppt",
            "ppt_document",
            "document",
            None
        ),
        (
            "HTML Document",
            "example.html",
            "html_document",
            "document",
            None
        ),
        (
            "CSV Document",
            "example.csv",
            "csv_document",
            "document",
            None
        ),
        (
            "JSON Document",
            "example.json",
            "json_document",
            "document",
            None
        ),
    ]

    for (
        description,
        file_name,
        output_name,
        read_mode,
        page_numbers
    ) in test_documents:

        file_path = os.path.join(
            testfiles_dir,
            file_name
        )

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
                read_mode=read_mode,
                page_numbers=page_numbers
            )

            print(f"\n=== {description.upper()} ===")
            print(result)

        except Exception as ex:
            print(
                f"\n{description} test failed:"
                f"\n{ex}"
            )

    # ------------------------------------------------------------------
    # Test queued background processing
    # ------------------------------------------------------------------

    queued_worker = FeatureWorker(
        tts_output_dir="./tts_output",
        from_lang="en",
        to_lang="de",
        thread_count=2
    )

    queued_worker.start_threads()

    queued_tests = [
        (
            os.path.join(image_dir, "lord_of _the _ring.png"),
            "queued_image",
            "document",
            None
        ),
        (
            os.path.join(testfiles_dir, "Fuchs_HA8.pdf"),
            "queued_pdf",
            "document",
            None
        ),
        (
            os.path.join(testfiles_dir, "example.docx"),
            "queued_docx",
            "document",
            None
        ),
        (
            os.path.join(testfiles_dir, "example.pptx"),
            "queued_pptx",
            "pages",
            [0, 1]
        ),
    ]

    for file_path, output_name, read_mode, page_numbers in queued_tests:
        if not os.path.exists(file_path):
            print(
                f"\nSkipping queued task: "
                f"file does not exist ({file_path})"
            )
            continue

        queued_worker.enqueue(
            input_file=file_path,
            ref_audio=ref_audio,
            filename=output_name,
            read_mode=read_mode,
            page_numbers=page_numbers
        )

    queued_worker.wait_until_done()
    queued_worker.stop_threads()


# -------------------------------------------------------------------------
# Application entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())