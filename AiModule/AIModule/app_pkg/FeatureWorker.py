import asyncio
import os
from typing import Union, List, Dict, Any

from app_pkg.Features.OCRFeature import OCRFeature
from app_pkg.Features.PDFReaderFeature import PDFReaderFeature
from app_pkg.Features.TextToSpeechFeature import TextToSpeechFeature
from app_pkg.Features.TranslatorFeature import TranslatorFeature
from app_pkg.Logger.Logging_setup import logger


class FeatureWorker:
    def __init__(self, tts_output_dir: str = "./output", from_lang: str = "de", to_lang: str = "en"):
        # TTS, OCR, Translator einmalig anlegen
        self.tts = TextToSpeechFeature(output_dir=tts_output_dir)
        self.ocr = OCRFeature()
        self.translator = TranslatorFeature()
        self.from_lang = from_lang
        self.to_lang = to_lang

    async def run(
        self,
        input_file: str,
        ref_audio: str = None,
        filename: str = "result",
        read_mode: str = "document",  # <--- NEU: nur für PDFs relevant
    ) -> Dict[str, Any]:
        """
        Entscheidet automatisch, ob OCR oder PDFReader genutzt wird,
        übersetzt optional und generiert Audio.
        Für PDFs steuert 'read_mode' das Chunking:
          - 'document'   -> ein Gesamt-Text  -> eine MP3
          - 'pages'      -> Liste pro Seite  -> mehrere MP3s
          - 'paragraphs' -> Liste pro Absatz -> mehrere MP3s
        """
        ext = os.path.splitext(input_file)[1].lower()

        # --- Bild -> OCR -> ein Text ---
        if ext in [".png", ".jpg", ".jpeg"]:
            logger.info("Start extracting text out of the image.")
            self.ocr.configure(picture_file_path=input_file)
            text: str = await self.ocr.process()
            logger.info("Finish extracting text out of the image.")

            # Optional: Übersetzung
            text = self._maybe_translate(text)

            # TTS Einzeldatei
            audio_path = self._tts_single(text=text, filename=filename)
            return {"text": text, "audio": audio_path}

        # --- PDF -> PDFReader ---
        elif ext == ".pdf":
            mode = read_mode if read_mode in {"document", "pages", "paragraphs"} else "document"
            logger.info(f"Start extracting text out of the pdf with read_mode='{mode}'.")
            pdf_reader = PDFReaderFeature()
            pdf_reader.configure(pdf_file_path=input_file, reader_mode=mode)
            pdf_result = await pdf_reader.process()
            logger.info("Finish extracting text out of the pdf.")

            # Fall A: document -> String -> Einzeldatei
            if mode == "document":
                if isinstance(pdf_result, list):
                    # Defensive: Falls der Reader unerwartet eine Liste liefert, joinen wir sauber.
                    text = "\n\n".join([str(x) for x in pdf_result if x])
                else:
                    text = str(pdf_result or "")

                # Optional: Übersetzung
                text = self._maybe_translate(text)

                # TTS Einzeldatei
                audio_path = self._tts_single(text=text, filename=filename)
                return {"text": text, "audio": audio_path}

            # Fall B: pages/paragraphs -> Liste -> Mehrfachdatei
            else:
                # Erwartet: Liste von Text-Chunks
                chunks: List[str] = pdf_result if isinstance(pdf_result, list) else [str(pdf_result or "")]
                # Vorab säubern
                chunks = [c for c in (str(x or "") for x in chunks) if c.strip()]

                if not chunks:
                    raise ValueError("PDF reader returned no content for the selected read_mode.")

                # Optional: pro Chunk übersetzen
                if self.from_lang != self.to_lang:
                    logger.info(f"Start translation per chunk from {self.from_lang} to {self.to_lang}.")
                    translated: List[str] = []
                    for idx, c in enumerate(chunks, start=1):
                        self.translator.configure(self.from_lang, self.to_lang, c)
                        translated.append(self.translator.process())
                    chunks = translated
                    logger.info("Finish translation per chunk.")

                # Pro Chunk eine Datei erzeugen: Dateinamen deterministisch suffixen
                audio_files: List[str] = []
                for i, c in enumerate(chunks, start=1):
                    # suffix anhand Modus
                    suffix = f"_p{i}" if mode == "pages" else f"_seg{i}"
                    audio_files.append(self._tts_single(text=c, filename=f"{filename}{suffix}"))

                return {"texts": chunks, "audios": audio_files}

        else:
            logger.error(f"Unsupported file type: {ext}")
            raise ValueError(f"Unsupported file type: {ext}")

    # ------------------- Hilfsmethoden -------------------

    def _maybe_translate(self, text: str) -> str:
        """Übersetzt den Text, wenn from_lang != to_lang."""
        if self.from_lang != self.to_lang:
            logger.info(f"Start translation of the text from {self.from_lang} to {self.to_lang}.")
            self.translator.configure(self.from_lang, self.to_lang, text)
            text = self.translator.process()
            logger.info("Finish translation of the text.")
        return text

    def _tts_single(self, text: str, filename: str) -> str:
        """Erzeugt genau eine Audio-Datei mit TTS und liefert deren Pfad."""
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


# Beispiel-Nutzung
async def main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(parent_dir, "app_pkg", "Resources", "Images", "lord_of _the _ring.png")
    pdf_path = os.path.join(parent_dir, "app_pkg", "Testfiles", "Fuchs_HA8.pdf")
    ref_audio = os.path.join(parent_dir, "app_pkg", "Resources", "Audio", "unbenannt.wav")

    worker = FeatureWorker(tts_output_dir="./tts_output", from_lang="en", to_lang="de")

    # Bild -> OCR -> TTS (ein File)
    result_img = await worker.run(
        input_file=image_path,
        ref_audio=ref_audio,
        filename="from_image",
        read_mode="document"  # irrelevant bei Bildern
    )
    print("Bild-Ergebnis:", result_img)

    # PDF -> gesamtes Dokument -> TTS (ein File)
    result_pdf_doc = await worker.run(
        input_file=pdf_path,
        ref_audio=ref_audio,
        filename="from_pdf_doc",
        read_mode="document"
    )
    print("PDF (document)-Ergebnis:", result_pdf_doc)

    # PDF -> seitenweise -> TTS (mehrere Files)
    result_pdf_pages = await worker.run(
        input_file=pdf_path,
        ref_audio=ref_audio,
        filename="from_pdf_pages",
        read_mode="pages"
    )
    print("PDF (pages)-Ergebnis:", result_pdf_pages)

    # PDF -> absatzweise -> TTS (mehrere Files)
    result_pdf_par = await worker.run(
        input_file=pdf_path,
        ref_audio=ref_audio,
        filename="from_pdf_paragraphs",
        read_mode="paragraphs"
    )
    print("PDF (paragraphs)-Ergebnis:", result_pdf_par)


if __name__ == "__main__":
    asyncio.run(main())