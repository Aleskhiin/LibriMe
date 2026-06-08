import os
import httpx


class BackendClient:
    def __init__(self):
        backend_url = os.environ.get("BACKEND_URL")
        if not backend_url:
            raise ValueError("BACKEND_URL environment variable is required but not set")
        self.base_url = backend_url.rstrip("/")

    def update_status(self, job_id: str, status: str, progress: int, output_path: str = "") -> None:
        url = f"{self.base_url}/jobs/{job_id}"
        response = httpx.put(
            url,
            params={
                "status": status,
                "progress": progress,
                "outputFilePath": output_path,
            },
            timeout=30.0,
        )
        response.raise_for_status()
