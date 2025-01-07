"""Module to handle media files from PetKit devices."""

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from typing import Any

from aiofiles import open as aio_open
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pypetkitapi.feeder_container import Feeder, RecordsType

_LOGGER = logging.getLogger(__name__)


@dataclass
class MediasFiles:
    """Dataclass for media files.
    Subclass of many other device dataclasses.
    """

    filename: str
    record_type: str
    url: str
    aes_key: str
    timestamp: str | None = None


async def extract_filename_from_url(url: str) -> str:
    """Extract the filename from the URL and format it as requested."""
    match = re.search(r"https?://[^/]+(/[^?]+)", url)
    if match:
        path = match.group(1)
        formatted_filename = path.replace("/", "_").lstrip("_").lower()
        return f"{formatted_filename}.jpg"
    raise ValueError(f"Failed to extract filename from URL: {url}")


class MediaHandler:
    """Class to find media files from PetKit devices."""

    def __init__(self, file_path: Path):
        """Initialize the class."""
        self.media_download_decode = MediaDownloadDecode(file_path)
        self.media_files: list[MediasFiles] = []

    async def get_last_image(self, device: Feeder) -> list[MediasFiles]:
        """Process device records and extract media info."""
        record_types = ["eat", "feed", "move", "pet"]
        self.media_files = []

        if not isinstance(device, Feeder):
            _LOGGER.error("Device is not a Feeder")
            return []

        if not device.device_records:
            _LOGGER.error("No device records found for feeder")
            return []

        for record_type in record_types:
            records = getattr(device.device_records, record_type, None)
            if records:
                self.media_files.extend(
                    await self._process_records(records, record_type)
                )
        return self.media_files

    async def _process_records(
        self, records: RecordsType, record_type: str
    ) -> list[MediasFiles]:
        """Process individual records and return media info."""
        media_files = []

        async def process_item(record_items):
            last_item = next(
                (
                    item
                    for item in reversed(record_items)
                    if item.preview and item.aes_key
                ),
                None,
            )
            if last_item:
                filename = await extract_filename_from_url(last_item.preview)
                await self.media_download_decode.get_file(
                    last_item.preview, last_item.aes_key
                )
                timestamp = (
                    last_item.eat_start_time
                    or last_item.completed_at
                    or last_item.timestamp
                    or None
                )
                media_files.append(
                    MediasFiles(
                        record_type=record_type,
                        filename=filename,
                        url=last_item.preview,
                        aes_key=last_item.aes_key,
                        timestamp=timestamp,
                    )
                )

        for record in records:
            if hasattr(record, "items"):
                await process_item(record.items)  # type: ignore[attr-defined]

        return media_files


class MediaDownloadDecode:
    """Class to download"""

    def __init__(self, download_path: Path):
        """Initialize the class."""
        self.download_path = download_path

    async def get_file(self, url: str, aes_key: str) -> bool:
        """Download a file from a URL and decrypt it."""
        # Check if the file already exists
        filename = await extract_filename_from_url(url)
        full_file_path = Path(self.download_path) / filename
        if full_file_path.exists():
            _LOGGER.debug("File already exist : %s don't need to download it", filename)
            return True

        # Download the file
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                _LOGGER.error(
                    "Failed to download %s, status code: %s", url, response.status
                )
                return False

            content = await response.read()

        encrypted_file_path = await self._save_file(content, f"{filename}.enc")
        # Decrypt the image
        decrypted_data = await self._decrypt_image_from_file(
            encrypted_file_path, aes_key
        )

        if decrypted_data:
            _LOGGER.debug("Decrypt was successful")
            await self._save_file(decrypted_data, filename)
            return True
        return False

    async def _save_file(self, content: bytes, filename: str) -> Path:
        """Save content to a file asynchronously and return the file path."""
        file_path = Path(self.download_path) / filename
        try:
            # Ensure the directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            async with aio_open(file_path, "wb") as file:
                await file.write(content)
            _LOGGER.debug("Save file OK : %s", file_path)
        except PermissionError as e:
            _LOGGER.error("Save file, permission denied %s: %s", file_path, e)
        except FileNotFoundError as e:
            _LOGGER.error("Save file, file/folder not found %s: %s", file_path, e)
        except OSError as e:
            _LOGGER.error("Save file, error saving file %s: %s", file_path, e)
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(
                "Save file, unexpected error saving file %s: %s", file_path, e
            )
        return file_path

    @staticmethod
    async def _decrypt_image_from_file(file_path: Path, aes_key: str) -> bytes | None:
        """Decrypt an image from a file using AES encryption.
        :param file_path: Path to the encrypted image file.
        :param aes_key: AES key used for decryption.
        :return: Decrypted image data.
        """
        try:
            if aes_key.endswith("\n"):
                aes_key = aes_key[:-1]
            key_bytes: bytes = aes_key.encode("utf-8")
            iv: bytes = b"\x61" * 16
            cipher: Any = AES.new(key_bytes, AES.MODE_CBC, iv)

            async with aio_open(file_path, "rb") as encrypted_file:
                encrypted_data: bytes = await encrypted_file.read()

            decrypted_data: bytes = unpad(
                cipher.decrypt(encrypted_data), AES.block_size  # type: ignore[attr-defined]
            )
        except Exception as e:  # noqa: BLE001
            logging.error("Error decrypting image from file %s: %s", file_path, e)
            return None
        if Path(file_path).exists():
            Path(file_path).unlink()
        return decrypted_data
