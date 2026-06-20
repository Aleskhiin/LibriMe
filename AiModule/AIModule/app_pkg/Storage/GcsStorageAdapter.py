import os
import tempfile

from google.cloud import storage


class GcsStorageAdapter:
    def __init__(self):
        bucket_name = os.environ.get("GCS_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable is required but not set")
        self.bucket_name = bucket_name
        self.client = storage.Client()

    def download(self, blob_name: str) -> str:
        ext = os.path.splitext(blob_name)[1]
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.close()
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(tmp.name)
        except Exception:
            os.remove(tmp.name)
            raise
        return tmp.name

    def upload(self, local_path: str, blob_name: str) -> None:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

    def upload_dir(self, local_dir: str, blob_prefix: str) -> None:
        for filename in os.listdir(local_dir):
            local_path = os.path.join(local_dir, filename)
            if os.path.isfile(local_path):
                self.upload(local_path, f"{blob_prefix}/{filename}")

    def cleanup(self, local_path: str) -> None:
        if os.path.exists(local_path):
            os.remove(local_path)
