import torch
from TTS.api import TTS
import os

def main():
    print("=== Coqui TTS – Offline Sprachgenerator ===")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"→ Gerät: {device}")

    # Pfad des Skripts (für .wav im gleichen Ordner)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    speaker_wav = os.path.join(script_dir, "unbenannt.wav")
    if not os.path.exists(speaker_wav):
        print(f"Datei {speaker_wav} wurde nicht gefunden!")
        speaker_wav = None

    # Modell laden (Single-Speaker, kein TorchCodec)
    print("Modell wird geladen ...")
    tts = TTS(
        model_name="tts_models/de/thorsten/tacotron2-DDC",  # funktioniert ohne TorchCodec
        gpu=(device == "cuda")
    )

    # Benutzertext
    text = input("\nGib den Text ein, der gesprochen werden soll:\n> ").strip()
    if not text:
        print("Kein Text eingegeben – Abbruch.")
        return

    # Ausgabedatei
    out_path = os.path.join(script_dir, "output.wav")

    print("\nGeneriere Sprache ...")

    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        file_path=out_path
    )

    print(f"\nFertig! Datei gespeichert als: {out_path}\n")

if __name__ == "__main__":
    main()
