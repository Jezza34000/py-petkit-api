"""Module to manage media files from PetKit devices."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import aiofiles
from aiofiles import open as aio_open
import aiofiles.os
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pypetkitapi import Feeder, Litter, PetKitClient, RecordType
from pypetkitapi.const import (
    FEEDER_WITH_CAMERA,
    LITTER_WITH_CAMERA,
    MediaType,
    RecordTypeLST,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MediaCloud:
    """Dataclass MediaFile.
    Represents a media file from a PetKit device.
    """

    event_id: str
    event_type: RecordType
    device_id: int
    user_id: int
    image: str | None
    video: str | None
    filepath: str
    aes_key: str
    timestamp: int


@dataclass
class MediaFile:
    """Dataclass MediaFile.
    Represents a media file into disk.
    """

    event_id: str
    device_id: int
    timestamp: int
    media_type: MediaType
    event_type: RecordType
    full_file_path: Path


class MediaManager:
    """Class to manage media files from PetKit devices."""

    media_table: list[MediaFile] = []

    async def get_all_media_files(
        self, devices: list[Feeder | Litter]
    ) -> list[MediaCloud]:
        """Get all media files from all devices and return a list of MediaFile."""
        media_files: list[MediaCloud] = []
        _LOGGER.debug("Processing media files for %s devices", len(devices))

        for device in devices:
            if isinstance(device, Feeder):
                if (
                    device.device_nfo
                    and device.device_nfo.device_type in FEEDER_WITH_CAMERA
                ):
                    media_files.extend(self._process_feeder(device))
                else:
                    _LOGGER.debug(
                        "Feeder %s does not support media file extraction",
                        device.name,
                    )
            elif isinstance(device, Litter):
                if (
                    device.device_nfo
                    and device.device_nfo.device_type in LITTER_WITH_CAMERA
                ):
                    media_files.extend(self._process_litter(device))
                else:
                    _LOGGER.debug(
                        "Litter %s does not support media file extraction",
                        device.name,
                    )

        return media_files

    async def get_all_media_files_disk(
        self, storage_path: Path, device_id: int
    ) -> None:
        """Construct the media file table for disk storage."""
        self.media_table.clear()

        today_str = datetime.now().strftime("%Y%m%d")
        base_path = storage_path / str(device_id) / today_str

        for record_type in RecordType:
            record_path = base_path / record_type
            snapshot_path = record_path / "snapshot"
            video_path = record_path / "video"

            # Regex pattern to match valid filenames
            valid_pattern = re.compile(rf"^(?:\d+_)?{device_id}_\d+\.(jpg|avi)$")

            # Populate the media table with event_id from filenames
            for subdir in [snapshot_path, video_path]:

                # Ensure the directories exist
                if not await aiofiles.os.path.exists(subdir):
                    _LOGGER.debug("Skip, path does not exist, %s", subdir)
                    continue

                _LOGGER.debug("Scanning directory %s", subdir)
                entries = await aiofiles.os.scandir(subdir)
                for entry in entries:
                    if entry.is_file() and valid_pattern.match(entry.name):
                        _LOGGER.debug("Entries found: %s", entry.name)
                        event_id = Path(entry.name).stem
                        timestamp = self._extraire_timestamp(str(entry.name))
                        media_type_str = Path(entry.name).suffix.lstrip(".")
                        try:
                            media_type = MediaType(media_type_str)
                        except ValueError:
                            _LOGGER.warning("Unknown media type: %s", media_type_str)
                            continue
                        self.media_table.append(
                            MediaFile(
                                event_id=event_id,
                                device_id=device_id,
                                timestamp=int(timestamp),
                                event_type=RecordType(record_type),
                                full_file_path=subdir / entry.name,
                                media_type=MediaType(media_type),
                            )
                        )

    @staticmethod
    def _extraire_timestamp(nom_fichier: str) -> int:
        match = re.search(r"_(\d+)\.[a-zA-Z0-9]+$", nom_fichier)
        if match:
            return int(match.group(1))
        return 0

    async def prepare_missing_files(
        self,
        media_cloud_list: list[MediaCloud],
        dl_type: list[MediaType] | None = None,
        event_type: list[RecordType] | None = None,
    ) -> list[MediaCloud]:
        """Compare MediaCloud objects with MediaFile objects and return a list of missing MediaCloud objects."""
        missing_media = []
        existing_event_ids = {media_file.event_id for media_file in self.media_table}

        for media_cloud in media_cloud_list:
            # Skip if event type is not in the filter
            if event_type and media_cloud.event_type not in event_type:
                continue

            # Check if the media file is missing
            is_missing = False
            if media_cloud.event_id not in existing_event_ids:
                is_missing = True  # Both image and video are missing
            else:
                # Check for missing image
                if (
                    media_cloud.image
                    and MediaType.IMAGE
                    in (dl_type or [MediaType.IMAGE, MediaType.VIDEO])
                    and not any(
                        media_file.event_id == media_cloud.event_id
                        and media_file.media_type == MediaType.IMAGE
                        for media_file in self.media_table
                    )
                ):
                    is_missing = True
                # Check for missing video
                if (
                    media_cloud.video
                    and MediaType.VIDEO
                    in (dl_type or [MediaType.IMAGE, MediaType.VIDEO])
                    and not any(
                        media_file.event_id == media_cloud.event_id
                        and media_file.media_type == MediaType.VIDEO
                        for media_file in self.media_table
                    )
                ):
                    is_missing = True

            if is_missing:
                missing_media.append(media_cloud)

        return missing_media

    def _process_feeder(self, feeder: Feeder) -> list[MediaCloud]:
        """Process media files for a Feeder device."""
        media_files: list[MediaCloud] = []
        records = feeder.device_records

        if not records:
            _LOGGER.debug("No records found for %s", feeder.name)
            return media_files

        for record_type in RecordTypeLST:
            record_list = getattr(records, record_type, [])
            for record in record_list:
                media_files.extend(
                    self._process_feeder_record(record, RecordType(record_type), feeder)
                )

        return media_files

    def _process_feeder_record(
        self, record, record_type: RecordType, device_obj: Feeder
    ) -> list[MediaCloud]:
        """Process individual feeder records."""
        media_files: list[MediaCloud] = []
        user_id = device_obj.user.id if device_obj.user else None
        feeder_id = device_obj.device_nfo.device_id if device_obj.device_nfo else None
        device_type = (
            device_obj.device_nfo.device_type if device_obj.device_nfo else None
        )
        cp_sub = (
            device_obj.cloud_product.subscribe if device_obj.cloud_product else None
        )

        if not feeder_id:
            _LOGGER.error("Missing feeder_id for record")
            return media_files

        if not record.items:
            return media_files

        for item in record.items:
            timestamp = self._get_timestamp(item)
            date_str = (
                datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
                if timestamp
                else "unknown"
            )
            if not item.event_id:
                # Skip feed event in the future
                _LOGGER.debug("Missing event_id for record item")
                continue
            if not user_id:
                _LOGGER.error("Missing user_id for record item")
                continue
            if not item.aes_key:
                _LOGGER.error("Missing aes_key for record item")
                continue
            if timestamp is None:
                _LOGGER.error("Missing timestamp for record item")
                continue

            filepath = f"{feeder_id}/{date_str}/{record_type.name.lower()}"
            media_files.append(
                MediaCloud(
                    event_id=item.event_id,
                    event_type=record_type,
                    device_id=feeder_id,
                    user_id=user_id,
                    image=item.preview,
                    video=self.construct_video_url(
                        device_type, item.media_api, user_id, cp_sub
                    ),
                    filepath=filepath,
                    aes_key=item.aes_key,
                    timestamp=self._get_timestamp(item),
                )
            )
        return media_files

    def _process_litter(self, litter: Litter) -> list[MediaCloud]:
        """Process media files for a Litter device."""
        media_files: list[MediaCloud] = []
        records = litter.device_records
        litter_id = litter.device_nfo.device_id if litter.device_nfo else None
        device_type = litter.device_nfo.device_type if litter.device_nfo else None
        user_id = litter.user.id if litter.user else None
        cp_sub = litter.cloud_product.subscribe if litter.cloud_product else None

        if not litter_id:
            _LOGGER.error("Missing litter_id for record")
            return media_files

        if not device_type:
            _LOGGER.error("Missing device_type for record")
            return media_files

        if not user_id:
            _LOGGER.error("Missing user_id for record")
            return media_files

        if not records:
            return media_files

        for record in records:
            timestamp = record.timestamp or None
            date_str = (
                datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
                if timestamp
                else "unknown"
            )
            if not record.event_id:
                _LOGGER.error("Missing event_id for record item")
                continue
            if not record.aes_key:
                _LOGGER.error("Missing aes_key for record item")
                continue
            if record.timestamp is None:
                _LOGGER.error("Missing timestamp for record item")
                continue

            filepath = f"{litter_id}/{date_str}/toileting"
            media_files.append(
                MediaCloud(
                    event_id=record.event_id,
                    event_type=RecordType.TOILETING,
                    device_id=litter_id,
                    user_id=user_id,
                    image=record.preview,
                    video=self.construct_video_url(
                        device_type, record.media_api, user_id, cp_sub
                    ),
                    filepath=filepath,
                    aes_key=record.aes_key,
                    timestamp=record.timestamp,
                )
            )
        return media_files

    @staticmethod
    def construct_video_url(
        device_type: str | None, media_url: str | None, user_id: int, cp_sub: int | None
    ) -> str | None:
        """Construct the video URL."""
        if not media_url or not user_id or cp_sub != 1:
            return None
        params = parse_qs(urlparse(media_url).query)
        param_dict = {k: v[0] for k, v in params.items()}
        return f"/{device_type}/cloud/video?startTime={param_dict.get("startTime")}&deviceId={param_dict.get("deviceId")}&userId={user_id}&mark={param_dict.get("mark")}"

    @staticmethod
    def _get_timestamp(item) -> int:
        """Extract timestamp from a record item and raise an exception if it is None."""
        timestamp = (
            item.timestamp
            or item.completed_at
            or item.eat_start_time
            or item.eat_end_time
            or item.start_time
            or item.end_time
            or item.time
            or None
        )
        if timestamp is None:
            raise ValueError("Can't find timestamp in record item")
        return timestamp


class DownloadDecryptMedia:
    """Class to download and decrypt media files from PetKit devices."""

    file_data: MediaCloud

    def __init__(self, download_path: Path, client: PetKitClient):
        """Initialize the class."""
        self.download_path = download_path
        self.client = client

    async def get_fpath(self, file_name: str) -> Path:
        """Return the full path of the file."""
        subdir = ""
        if file_name.endswith(".jpg"):
            subdir = "snapshot"
        elif file_name.endswith(".avi"):
            subdir = "video"
        return Path(self.download_path / self.file_data.filepath / subdir / file_name)

    async def download_file(
        self, file_data: MediaCloud, file_type: MediaType | None
    ) -> None:
        """Get image and video file"""
        _LOGGER.debug("Downloading media file %s", file_data.event_id)
        self.file_data = file_data

        if self.file_data.image and (file_type is None or file_type == MediaType.IMAGE):
            # Download image file
            await self._get_file(
                self.file_data.image,
                self.file_data.aes_key,
                f"{self.file_data.event_id}.jpg",
            )

        if self.file_data.video and (file_type is None or file_type == MediaType.VIDEO):
            # Download video file
            await self._get_video_m3u8()

    async def _get_video_m3u8(self) -> None:
        """Iterate through m3u8 file and return all the ts file urls"""
        aes_key, iv_key, segments_lst = await self._get_m3u8_segments()

        if aes_key is None or iv_key is None or not segments_lst:
            _LOGGER.debug("Can't download video file %s", self.file_data.event_id)
            return

        segment_files = []

        if len(segments_lst) == 1:
            await self._get_file(
                segments_lst[0], aes_key, f"{self.file_data.event_id}.avi"
            )
            return

        for index, segment in enumerate(segments_lst, start=1):
            segment_file = await self._get_file(
                segment, aes_key, f"{index}_{self.file_data.event_id}.avi"
            )
            if segment_file:
                segment_files.append(
                    await self.get_fpath(f"{index}_{self.file_data.event_id}.avi")
                )

        if not segment_files:
            _LOGGER.error("No segment files found")
        elif len(segment_files) == 1:
            _LOGGER.debug("Single file segment, no need to concatenate")
        elif len(segment_files) > 1:
            _LOGGER.debug("Concatenating segments %s", len(segment_files))
            await self._concat_segments(segment_files, f"{self.file_data.event_id}.avi")

    async def _get_m3u8_segments(self) -> tuple[str | None, str | None, list[str]]:
        """Extract the segments from a m3u8 file.
        :return: Tuple of AES key, IV key, and list of segment URLs
        """
        if not self.file_data.video:
            raise ValueError("Missing video URL")
        video_data = await self.client.get_cloud_video(self.file_data.video)

        if not video_data:
            return None, None, []

        media_api = video_data.get("mediaApi", None)
        if not media_api:
            _LOGGER.error("Missing mediaApi in video data")
            raise ValueError("Missing mediaApi in video data")
        return await self.client.extract_segments_m3u8(str(media_api))

    async def _get_file(self, url: str, aes_key: str, full_filename: str) -> bool:
        """Download a file from a URL and decrypt it."""

        full_file_path = await self.get_fpath(full_filename)
        if full_file_path.exists():
            _LOGGER.debug("File already exist : %s don't re-download it", full_filename)
            return True

        # Download the file
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                _LOGGER.error(
                    "Failed to download %s, status code: %s", url, response.status
                )
                return False

            content = await response.read()

        encrypted_file_path = await self._save_file(content, f"{full_filename}.enc")
        # Decrypt the image
        decrypted_data = await self._decrypt_file(encrypted_file_path, aes_key)

        if decrypted_data:
            _LOGGER.debug("Decrypt was successful")
            await self._save_file(decrypted_data, full_filename)
            return True
        return False

    async def _save_file(self, content: bytes, filename: str) -> Path:
        """Save content to a file asynchronously and return the file path."""
        file_path = await self.get_fpath(filename)
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
    async def _decrypt_file(file_path: Path, aes_key: str) -> bytes | None:
        """Decrypt a file using AES encryption.
        :param file_path: Path to the encrypted file.
        :param aes_key: AES key used for decryption.
        :return: Decrypted bytes data.
        """
        aes_key = aes_key.removesuffix("\n")
        key_bytes: bytes = aes_key.encode("utf-8")
        iv: bytes = b"\x61" * 16
        cipher: Any = AES.new(key_bytes, AES.MODE_CBC, iv)

        async with aio_open(file_path, "rb") as encrypted_file:
            encrypted_data: bytes = await encrypted_file.read()

        decrypted_data: bytes = cipher.decrypt(encrypted_data)

        try:
            decrypted_data = unpad(decrypted_data, AES.block_size)
        except ValueError as e:
            _LOGGER.debug("Warning: Padding error occurred, ignoring error: %s", e)

        if Path(file_path).exists():
            Path(file_path).unlink()
        return decrypted_data

    async def _concat_segments(self, ts_files: list[Path], output_file):
        """Concatenate a list of .ts segments into a single output file without using a temporary file.

        :param ts_files: List of absolute paths of .ts files
        :param output_file: Path of the output file (e.g., "output.mp4")
        """
        full_output_file = await self.get_fpath(output_file)
        if full_output_file.exists():
            _LOGGER.debug(
                "Output file already exists: %s, skipping concatenation.", output_file
            )
            await self._delete_segments(ts_files)
            return

        # Build the argument for `ffmpeg` with the files formatted for the command line
        concat_input = "|".join(str(file) for file in ts_files)
        command = [
            "ffmpeg",
            "-i",
            f"concat:{concat_input}",
            "-c",
            "copy",
            "-bsf:a",
            "aac_adtstoasc",
            str(full_output_file),
        ]

        try:
            # Run the subprocess asynchronously
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                _LOGGER.debug("File successfully concatenated: %s", full_output_file)
                await self._delete_segments(ts_files)
            else:
                _LOGGER.error(
                    "Error during concatenation: %s\nStdout: %s\nStderr: %s",
                    process.returncode,
                    stdout.decode().strip(),
                    stderr.decode().strip(),
                )
        except FileNotFoundError as e:
            _LOGGER.error("Error during concatenation: %s", e)
        except OSError as e:
            _LOGGER.error("OS error during concatenation: %s", e)

    async def _delete_segments(self, ts_files: list[Path]) -> None:
        """Delete all segment files after concatenation."""
        for file in ts_files:
            if file.exists():
                try:
                    file.unlink()
                    _LOGGER.debug("Deleted segment file: %s", file)
                except OSError as e:
                    _LOGGER.debug("Error deleting segment file %s: %s", file, e)
            else:
                _LOGGER.debug("Segment file not found: %s", file)
