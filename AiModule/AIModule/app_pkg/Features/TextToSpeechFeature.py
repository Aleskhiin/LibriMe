import torch
from TTS.api import TTS
import os
from .BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger

class TextToSpeechFeature(BaseFeature):
    """
    TextToSpeechFeature provides functionality for text-to-speech generation using the CoquiTTs.
    It creates audio files from text input, using a language model to generate speech.
    """

    def __init__(self, model="F5TTS_v1_Base", output_dir="./output"):
        """
        Initialize the TTS feature:
        - Creates output directory if it doesn't exist.
        - Selects device (CUDA if available, else CPU).
        - Loads the F5-TTS model.
        """
        self.model = model
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # Ensure output directory exists

        # Select device: CUDA for GPU acceleration if available, otherwise CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # TODO: Implement dynamic model loading based on self.model

        self.tts = TTS(
            model_name="tts_models/de/thorsten/tacotron2-DDC",  # funktioniert ohne TorchCodec
            gpu=(self.device == "cuda")
        )

    def process(self) -> str:
        """
        Perform voice cloning:
        - Takes reference audio and text.
        - Generates new audio with the same voice characteristics.
        Args:
            ref_text (str): Text spoken in reference audio.
            gen_text (str): Text to generate with cloned voice.
            filename (str): Output filename (without extension).
            remove_silence (bool): Remove silence from generated audio.
        Returns:
            str: Path to generated audio file.
        """

        output_path = os.path.join(self.output_dir, f"{self.filename}.wav")

        logger.info("Starting voice cloning with F5-TTS...")
        logger.info(f"Target Text:     {self.gen_text}")


        self.tts.tts_to_file(
            text=self.gen_text,
            file_path=output_path
        )

        logger.info(f"Audio saved at: {output_path}")
        return output_path
    
    def set_LanguageModel(self, model: str):
        logger.info(f"Set the language Model to '{model}'")

        if model == "de":
            self.tts = TTS(
                model_name="tts_models/de/thorsten/tacotron2-DDC",
                gpu=(self.device == "cuda")
            )
        elif model == "en":
            self.tts = TTS(
                model_name="tts_models/en/ljspeech/tacotron2-DDC",
                gpu=(self.device == "cuda")
            )
        elif model == "fr":
            self.tts = TTS(
                model_name="tts_models/fr/css10/vits",
                gpu=(self.device == "cuda")
            )
        else:
            raise ValueError(f"Unsupported TTS language: {model}")

    def configure(self,               
                        gen_text: str,
                        filename: str = "output",
                        output_dir: str = "./output",
                        language: str = "en"):
        logger.info("Configure TextToSpeechFeature.")

        self.gen_text = gen_text
        self.filename = filename
        self.output_dir = output_dir 

        self.set_LanguageModel(language) 


def main():
    """
    Example usage:
    - Define reference audio and text.
    - Initialize TextToSpeechFeature.
    - Generate new audio with cloned voice.
    """

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ref_audio = os.path.join(parent_dir, "Resources", "Audio", "unbenannt.wav")
    output_dir = os.path.join(parent_dir, "output")

    tts = TextToSpeechFeature()

    gen_text = "Das ist ein Text, der von einer KI generiert wurde! Es ist erstaunlich, wie gut moderne Modelle Sprache erzeugen können."

    tts.configure(gen_text, ref_audio, filename="result", output_dir=output_dir)

    tts.process()


if __name__ == "__main__":
    main()