"""Module to handle media files from PetKit devices."""

from dataclasses import dataclass
import logging
from pathlib import Path
import re

from aiofiles import open as aio_open
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pypetkitapi.feeder_container import Feeder, RecordsItems

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

    def __init__(self, device: Feeder, file_path: str):
        """Initialize the class."""
        self.device = device
        self.media_download_decode = MediaDownloadDecode(file_path)
        self.media_files: list[MediasFiles] = []

    async def get_last_image(self) -> list[MediasFiles]:
        """Process device records and extract media info."""
        record_types = ["eat", "feed", "move", "pet"]
        self.media_files = []

        if not self.device.device_records:
            _LOGGER.error("No device records found for feeder")
            return []

        for record_type in record_types:
            records = getattr(self.device.device_records, record_type, None)
            if records:
                self.media_files.extend(
                    await self._process_records(records, record_type)
                )

        return self.media_files

    async def _process_records(
        self, records: RecordsItems, record_type: str
    ) -> list[MediasFiles]:
        """Process individual records and return media info."""
        media_files = []

        if record_type == "feed":
            for record in reversed(records):
                if record.items:
                    last_item = next(
                        (
                            item
                            for item in reversed(record.items)
                            if item.preview and item.aes_key
                        ),
                        None,
                    )
                    if last_item:
                        filename = await extract_filename_from_url(last_item.preview)
                        await self.media_download_decode.get_file(
                            last_item.preview, last_item.aes_key
                        )
                        media_files.append(
                            MediasFiles(
                                record_type=record_type,
                                filename=filename,
                                url=last_item.preview,
                                aes_key=last_item.aes_key,
                            )
                        )
                        return media_files
        else:
            for record in records:
                if record.items:
                    last_item = record.items[-1]
                    preview_url = last_item.preview
                    aes_key = last_item.aes_key

                    if preview_url and aes_key:
                        filename = await extract_filename_from_url(preview_url)
                        await self.media_download_decode.get_file(preview_url, aes_key)
                        media_files.append(
                            MediasFiles(
                                record_type=record_type,
                                filename=filename,
                                url=preview_url,
                                aes_key=aes_key,
                            )
                        )
        return media_files


class MediaDownloadDecode:
    """Class to download"""

    def __init__(self, download_path: str):
        """Initialize the class."""
        self.download_path = download_path

    async def get_file(self, url: str, aes_key: str) -> bool:
        """Download a file from a URL and decrypt it."""
        try:
            # Check if the file already exists
            filename = await extract_filename_from_url(url)
            full_file_path = Path(self.download_path) / filename
            if full_file_path.exists():
                _LOGGER.debug(
                    "File already exist : %s don't need to download it", filename
                )
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
                    Path(encrypted_file_path).unlink()
                    return True
                _LOGGER.error("Failed to decrypt %s", encrypted_file_path)
        except Exception as e:  # noqa: BLE001
            _LOGGER.error("Error get media file from %s: %s", url, e)
        return False

    async def _save_file(self, content: bytes, filename: str) -> Path:
        """Save content to a file asynchronously and return the file path."""
        file_path = Path(self.download_path) / filename
        try:
            async with aio_open(file_path, "wb") as file:
                await file.write(content)
            _LOGGER.debug("Saved file: %s", file_path)
        except OSError as e:
            _LOGGER.error("Error saving file %s: %s", file_path, e)
        return file_path

    async def _decrypt_image_from_file(
        self, file_path: Path, aes_key: str
    ) -> bytes | None:
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
            cipher: AES = AES.new(key_bytes, AES.MODE_CBC, iv)

            async with aio_open(file_path, "rb") as encrypted_file:
                encrypted_data: bytes = await encrypted_file.read()

            decrypted_data: bytes = unpad(
                cipher.decrypt(encrypted_data), AES.block_size
            )
        except Exception as e:  # noqa: BLE001
            logging.error("Error decrypting image from file %s: %s", file_path, e)
            return None
        return decrypted_data
