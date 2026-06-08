import asyncio
import base64
import json
import os
import shutil
import tempfile
from typing import Dict, Any

from app_pkg.BackendClient import BackendClient
from app_pkg.FeatureWorker import FeatureWorker
from app_pkg.Logger.Logging_setup import logger
from app_pkg.Storage.GcsStorageAdapter import GcsStorageAdapter

SPLITTING_MAP = {
    "DOCUMENT": "document",
    "PAGE": "pages",
    "PARAGRAPH": "paragraphs",
}


def _lang_code(lang_type: str) -> str:
    return lang_type.split("_")[0].lower()


class PubSubJobHandler:
    def __init__(self, gcs: GcsStorageAdapter = None, backend: BackendClient = None):
        self.gcs = gcs or GcsStorageAdapter()
        self.backend = backend or BackendClient()

    def parse_message(self, push_body: Dict[str, Any]) -> Dict[str, Any]:
        data_b64 = push_body["message"]["data"]
        return json.loads(base64.b64decode(data_b64))

    def handle(self, push_body: Dict[str, Any]) -> None:
        msg = self.parse_message(push_body)
        job_id = msg["jobID"]
        data_path = msg["dataPath"]
        from_lang = _lang_code(msg["fileLanguage"])
        to_lang = _lang_code(msg["translationLanguage"])
        read_mode = SPLITTING_MAP.get(msg["splittingType"], "document")

        self.backend.update_status(job_id, "RUNNING", 0)

        tmp_dir = tempfile.mkdtemp()
        local_input = None

        try:
            local_input = self.gcs.download(data_path)

            worker = FeatureWorker(
                tts_output_dir=tmp_dir,
                from_lang=from_lang,
                to_lang=to_lang,
            )

            try:
                result = asyncio.run(worker.run(
                    input_file=local_input,
                    read_mode=read_mode,
                    filename=job_id,
                ))
            except Exception as e:
                logger.error(f"Job {job_id} processing failed: {e}")
                self.backend.update_status(job_id, "FAILED", 0)
                return

            if "audio" in result:
                audio_path = result["audio"]
                blob_name = f"{job_id}/{os.path.basename(audio_path)}"
                self.gcs.upload(audio_path, blob_name)
                output_path = blob_name
            else:
                self.gcs.upload_dir(tmp_dir, job_id)
                output_path = f"{job_id}/"

            self.backend.update_status(job_id, "COMPLETED", 100, output_path)

        finally:
            if local_input:
                self.gcs.cleanup(local_input)
            shutil.rmtree(tmp_dir, ignore_errors=True)
