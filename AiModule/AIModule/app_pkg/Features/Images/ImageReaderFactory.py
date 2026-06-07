import asyncio
import os
from pathlib import Path

from .OCRImageReader import OCRImageReader


class ImageReaderFactory:
    """
    Factory for image readers.
    """

    _readers = {
        ".png": OCRImageReader,
        ".jpg": OCRImageReader,
        ".jpeg": OCRImageReader,
        ".bmp": OCRImageReader,
        ".tif": OCRImageReader,
        ".tiff": OCRImageReader,
        ".webp": OCRImageReader,
    }

    @classmethod
    def create_reader(cls, file_path: str):
        """
        Creates the matching image reader.

        Args:
            file_path: Path to the image.

        Returns:
            Image reader instance.
        """

        suffix = Path(file_path).suffix.lower()

        reader_cls = cls._readers.get(suffix)

        if not reader_cls:
            raise ValueError(
                f"Unsupported image type: {suffix}"
            )

        return reader_cls()

    @classmethod
    def supported_extensions(cls):
        """
        Returns all supported image extensions.
        """

        return list(cls._readers.keys())


# -------------------------------------------------------------------------
# Manual test entry point
# -------------------------------------------------------------------------

async def main():
    """
    Tests the image reader factory.
    """

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    test_dir = os.path.join(
        base_dir,
        "Resources",
        "Images"
    )

    test_files = [
        "example.png",
        "example.jpg",
        "example.jpeg",
        "example.bmp",
        "example.webp"
    ]

    for file_name in test_files:

        file_path = os.path.join(
            test_dir,
            file_name
        )

        if not os.path.exists(file_path):
            print(
                f"Skipping {file_name}"
            )
            continue

        reader = ImageReaderFactory.create_reader(
            file_path
        )

        reader.configure(
            file_path=file_path
        )

        result = await reader.process()

        print(
            f"\n=== {file_name} ==="
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())