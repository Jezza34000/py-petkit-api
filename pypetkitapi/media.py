"""Module to manage media files from PetKit devices."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
import os
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

from pypetkitapi import Feeder, Litter, PetKitClient, RecordsItems, RecordType
from pypetkitapi.const import (
    FEEDER_WITH_CAMERA,
    LITTER_WITH_CAMERA,
    MediaType,
    PetkitEndpoint,
    RecordTypeLST,
)
from pypetkitapi.litter_container import LitterRecord

_LOGGER = logging.getLogger(__name__)


@dataclass
class MediaCloud:
    """Dataclass MediaCloud.
    Represents a media file from Petkit API.
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

    async def gather_all_media_from_cloud(
        self, devices: list[Feeder | Litter]
    ) -> list[MediaCloud]:
        """Get all media files from all devices and return a list of MediaCloud.
        :param devices: List of devices
        :return: List of MediaCloud objects
        """
        media_files: list[MediaCloud] = []
        _LOGGER.debug("Processing media files for %s devices", len(devices))

        for device in devices:
            if isinstance(device, Feeder):
                if (
                    device.device_nfo
                    and device.device_nfo.device_type in FEEDER_WITH_CAMERA
                ):
                    media_files.extend(await self._process_feeder(device))
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
                    media_files.extend(await self._process_litter(device))
                else:
                    _LOGGER.debug(
                        "Litter %s does not support media file extraction",
                        device.name,
                    )

        return media_files

    async def gather_all_media_from_disk(
        self, storage_path: Path, device_id: int
    ) -> list[MediaFile]:
        """Construct the media file table for disk storage."""
        self.media_table.clear()

        today_str = datetime.now().strftime("%Y%m%d")
        base_path = storage_path / str(device_id) / today_str

        _LOGGER.debug("Populating files from directory %s", base_path)

        valid_pattern = re.compile(
            rf"^{device_id}_\d+\.({MediaType.IMAGE}|{MediaType.VIDEO})$"
        )

        for record_type in RecordType:
            record_path = base_path / record_type
            subdirs = [record_path / "snapshot", record_path / "video"]
            for subdir in subdirs:
                await self._process_subdir(
                    subdir, device_id, record_type, valid_pattern
                )

        _LOGGER.debug("OK, Media table populated with %s files", len(self.media_table))
        return self.media_table

    async def _process_subdir(
        self,
        subdir: Path,
        device_id: int,
        record_type: RecordType,
        valid_pattern: re.Pattern,
    ) -> None:
        """Process a subdirectory to collect media files."""
        if not await aiofiles.os.path.exists(subdir):
            _LOGGER.debug("Path does not exist, skip: %s", subdir)
            return

        _LOGGER.debug("Scanning files into: %s", subdir)
        entries = await aiofiles.os.scandir(subdir)
        for entry in entries:
            media_file = await self._create_media_file(
                entry, device_id, record_type, subdir, valid_pattern
            )
            if media_file:
                self.media_table.append(media_file)

    @staticmethod
    async def _create_media_file(
        entry: os.DirEntry,
        device_id: int,
        record_type: RecordType,
        subdir: Path,
        valid_pattern: re.Pattern,
    ) -> MediaFile | None:
        """Create a MediaFile from a directory entry if valid."""
        if not entry.is_file() or not valid_pattern.match(entry.name):
            return None

        try:
            stem = Path(entry.name).stem
            parts = stem.split("_")
            timestamp = int(parts[1])
            media_type_str = Path(entry.name).suffix.lstrip(".")
            media_type = MediaType(media_type_str)
        except (ValueError, IndexError) as e:
            _LOGGER.warning("Invalid file %s: %s", entry.name, str(e))
            return None

        return MediaFile(
            event_id=stem,
            device_id=device_id,
            timestamp=timestamp,
            media_type=media_type,
            event_type=record_type,
            full_file_path=subdir / entry.name,
        )

    async def list_missing_files(
        self,
        media_cloud_list: list[MediaCloud],
        dl_type: list[MediaType] | None = None,
        event_type: list[RecordType] | None = None,
    ) -> list[MediaCloud]:
        """Compare MediaCloud objects with MediaFile objects and return missing ones."""
        if not dl_type or not event_type:
            _LOGGER.debug("Missing dl_type or event_type, no downloads")
            return []

        existing_event_ids = {media_file.event_id for media_file in self.media_table}
        return [
            mc
            for mc in media_cloud_list
            if self._should_process_media(mc, event_type, dl_type, existing_event_ids)
        ]

    def _should_process_media(
        self,
        media_cloud: MediaCloud,
        event_filter: list[RecordType],
        dl_types: list[MediaType],
        existing_ids: set[str],
    ) -> bool:
        """Determine if a media should be processed as missing."""
        if self._should_skip_event_type(media_cloud.event_type, event_filter):
            return False

        return self._is_media_missing(media_cloud, dl_types, existing_ids)

    @staticmethod
    def _should_skip_event_type(
        event_type: RecordType, event_filter: list[RecordType]
    ) -> bool:
        """Check if event type should be skipped."""
        if event_type not in event_filter:
            _LOGGER.debug("Skipping filtered event type: %s", event_type)
            return True
        return False

    def _is_media_missing(
        self, media_cloud: MediaCloud, dl_types: list[MediaType], existing_ids: set[str]
    ) -> bool:
        """Check if any media type is missing."""
        missing_image = self._is_image_missing(media_cloud, dl_types, existing_ids)
        missing_video = self._is_video_missing(media_cloud, dl_types, existing_ids)

        if missing_image or missing_video:
            self._log_missing_details(media_cloud, missing_image, missing_video)
            return True
        return False

    def _is_image_missing(
        self, media_cloud: MediaCloud, dl_types: list[MediaType], existing_ids: set[str]
    ) -> bool:
        """Check if image is missing."""
        return bool(
            media_cloud.image
            and MediaType.IMAGE in dl_types
            and not self._media_exists(
                media_cloud.event_id, MediaType.IMAGE, existing_ids
            )
        )

    def _is_video_missing(
        self, media_cloud: MediaCloud, dl_types: list[MediaType], existing_ids: set[str]
    ) -> bool:
        """Check if video is missing."""
        return bool(
            media_cloud.video
            and MediaType.VIDEO in dl_types
            and not self._media_exists(
                media_cloud.event_id, MediaType.VIDEO, existing_ids
            )
        )

    def _media_exists(
        self, event_id: str, media_type: MediaType, existing_ids: set[str]
    ) -> bool:
        """Check if media exists in local storage."""
        for mf in self.media_table:
            if event_id in existing_ids and mf.media_type == media_type:
                return True
        return False

    @staticmethod
    def _log_missing_details(
        media_cloud: MediaCloud, missing_image: bool, missing_video: bool
    ) -> None:
        """Log details about missing media."""
        details = []
        if missing_image:
            details.append("IMAGE")
        if missing_video:
            details.append("VIDEO")
        _LOGGER.debug(
            "Media missing for event : %s %s", media_cloud.event_id, " + ".join(details)
        )

    async def _process_feeder(self, feeder: Feeder) -> list[MediaCloud]:
        """Process media files for a Feeder device.
        :param feeder: Feeder device object
        :return: List of MediaCloud objects for the device
        """
        media_files: list[MediaCloud] = []
        records = feeder.device_records

        if not records:
            _LOGGER.debug("No records found for %s", feeder.name)
            return media_files

        for record_type in RecordTypeLST:
            record_list = getattr(records, record_type, [])
            for record in record_list:
                media_files.extend(
                    await self._process_feeder_record(
                        record, RecordType(record_type), feeder
                    )
                )

        return media_files

    async def _process_feeder_record(
        self, record, record_type: RecordType, device_obj: Feeder
    ) -> list[MediaCloud]:
        """Process individual feeder records.
        :param record: Record object
        :param record_type: Record type
        :param device_obj: Feeder device object
        :return: List of MediaCloud objects for the record
        """
        media_files: list[MediaCloud] = []
        user_id = device_obj.user.id if device_obj.user else None
        feeder_id = device_obj.device_nfo.device_id if device_obj.device_nfo else None
        device_type = (
            device_obj.device_nfo.device_type if device_obj.device_nfo else None
        )
        cp_sub = self.is_subscription_active(device_obj)

        if not feeder_id or not record.items:
            _LOGGER.debug("Missing feeder_id or items for record")
            return media_files

        for item in record.items:
            if not isinstance(item, RecordsItems):
                _LOGGER.debug("Record is empty")
                continue
            timestamp = await self._get_timestamp(item)
            if timestamp is None:
                _LOGGER.warning("Missing timestamp for record item")
                continue
            if not item.event_id or not item.aes_key:
                # Skip feed event in the future
                _LOGGER.debug(
                    "Missing event_id or aes_key for record item (probably a feed event not yet completed, or uploaded)"
                )
                continue
            if not user_id:
                _LOGGER.warning("Missing user_id for record item")
                continue

            date_str = await self.get_date_from_ts(timestamp)
            filepath = f"{feeder_id}/{date_str}/{record_type.name.lower()}"
            media_files.append(
                MediaCloud(
                    event_id=item.event_id,
                    event_type=record_type,
                    device_id=feeder_id,
                    user_id=user_id,
                    image=item.preview,
                    video=await self.construct_video_url(
                        device_type, item, user_id, cp_sub
                    ),
                    filepath=filepath,
                    aes_key=item.aes_key,
                    timestamp=timestamp,
                )
            )
        return media_files

    async def _process_litter(self, litter: Litter) -> list[MediaCloud]:
        """Process media files for a Litter device.
        :param litter: Litter device object
        :return: List of MediaCloud objects for the device
        """
        media_files: list[MediaCloud] = []
        records = litter.device_records
        litter_id = litter.device_nfo.device_id if litter.device_nfo else None
        device_type = litter.device_nfo.device_type if litter.device_nfo else None
        user_id = litter.user.id if litter.user else None
        cp_sub = self.is_subscription_active(litter)

        if not litter_id or not device_type or not user_id:
            _LOGGER.warning(
                "Missing one or more of mandatory information : litter_id/device_id/user_id for record"
            )
            return media_files

        if not records:
            _LOGGER.debug("No records found for %s", litter.name)
            return media_files

        for record in records:
            if not isinstance(record, LitterRecord):
                _LOGGER.debug("Record is empty")
                continue
            if not record.event_id or not record.aes_key:
                _LOGGER.debug("Missing event_id or aes_key for record item")
                continue
            if record.timestamp is None:
                _LOGGER.debug("Missing timestamp for record item")
                continue

            timestamp = record.timestamp or None
            date_str = await self.get_date_from_ts(timestamp)

            filepath = f"{litter_id}/{date_str}/toileting"
            media_files.append(
                MediaCloud(
                    event_id=record.event_id,
                    event_type=RecordType.TOILETING,
                    device_id=litter_id,
                    user_id=user_id,
                    image=record.preview,
                    video=await self.construct_video_url(
                        device_type, record, user_id, cp_sub
                    ),
                    filepath=filepath,
                    aes_key=record.aes_key,
                    timestamp=record.timestamp,
                )
            )
        return media_files

    @staticmethod
    def is_subscription_active(device: Feeder | Litter) -> bool:
        """Check if the subscription is active based on the work_indate timestamp.
        :param device: Device object
        :return: True if the subscription is active, False otherwise
        """
        if device.cloud_product and device.cloud_product.work_indate:
            return (
                datetime.fromtimestamp(device.cloud_product.work_indate)
                > datetime.now()
            )
        return False

    @staticmethod
    async def get_date_from_ts(timestamp: int | None) -> str:
        """Get date from timestamp.
        :param timestamp: Timestamp
        :return: Date string
        """
        if not timestamp:
            return "unknown"
        return datetime.fromtimestamp(timestamp).strftime("%Y%m%d")

    @staticmethod
    async def construct_video_url(
        device_type: str | None,
        event_data: LitterRecord | RecordsItems,
        user_id: int,
        cp_sub: bool | None,
    ) -> str | None:
        """Construct the video URL.
        :param device_type: Device type
        :param event_data: LitterRecord | RecordsItems
        :param user_id: User ID
        :param cp_sub: Cpsub value
        :return: Constructed video URL
        """
        if not hasattr(event_data, "media_api") or not user_id or not cp_sub:
            return None
        params = parse_qs(str(urlparse(event_data.media_api).query))
        param_dict = {k: v[0] for k, v in params.items()}
        url = f"/{device_type}/{PetkitEndpoint.CLOUD_VIDEO}?startTime={param_dict.get('startTime')}&deviceId={param_dict.get('deviceId')}&userId={user_id}&mark={param_dict.get('mark')}"
        if hasattr(event_data, "eat_end_time"):
            # Special case for Eat video (need to add endTime)
            url += f"&endTime={event_data.eat_end_time}"
        return url

    @staticmethod
    async def _get_timestamp(item) -> int | None:
        """Extract timestamp from a record item and raise an exception if it is None.
        :param item: Record item
        :return: Timestamp
        """
        return (
            item.timestamp
            or item.completed_at
            or item.eat_start_time
            or item.eat_end_time
            or item.start_time
            or item.end_time
            or item.time
            or None
        )


class DownloadDecryptMedia:
    """Class to download and decrypt media files from PetKit devices."""

    file_data: MediaCloud

    def __init__(self, download_path: Path, client: PetKitClient):
        """Initialize the class."""
        self.download_path = download_path
        self.client = client

    async def get_fpath(self, file_name: str) -> Path:
        """Return the full path of the file.
        :param file_name: Name of the file.
        :return: Full path of the file.
        """
        subdir = ""
        if file_name.endswith(MediaType.IMAGE):
            subdir = "snapshot"
        elif file_name.endswith(MediaType.VIDEO):
            subdir = "video"
        return Path(self.download_path / self.file_data.filepath / subdir / file_name)

    async def download_file(
        self, file_data: MediaCloud, file_type: list[MediaType] | None
    ) -> None:
        """Get image and video files."""
        self.file_data = file_data
        if not file_type:
            file_type = []
        filename = f"{self.file_data.device_id}_{self.file_data.timestamp}"

        if self.file_data.image and MediaType.IMAGE in file_type:
            full_filename = f"{filename}.{MediaType.IMAGE}"
            if await self.not_existing_file(full_filename):
                # Image download
                _LOGGER.debug("Download image file (event id: %s)", file_data.event_id)
                await self._get_file(
                    self.file_data.image,
                    self.file_data.aes_key,
                    f"{self.file_data.device_id}_{self.file_data.timestamp}.{MediaType.IMAGE}",
                )

        if self.file_data.video and MediaType.VIDEO in file_type:
            if await self.not_existing_file(f"{filename}.{MediaType.VIDEO}"):
                # Video download
                _LOGGER.debug("Download video file (event id: %s)", file_data.event_id)
                await self._get_video_m3u8()

    async def not_existing_file(self, file_name: str) -> bool:
        """Check if the file already exists.
        :param file_name: Filename
        :return: True if the file exists, False otherwise.
        """
        full_file_path = await self.get_fpath(file_name)
        if full_file_path.exists():
            _LOGGER.debug(
                "File already exist : %s don't re-download it", full_file_path
            )
            return False
        return True

    async def _get_video_m3u8(self) -> None:
        """Iterate through m3u8 file and return all the ts file URLs."""
        aes_key, iv_key, segments_lst = await self._get_m3u8_segments()
        file_name = (
            f"{self.file_data.device_id}_{self.file_data.timestamp}.{MediaType.VIDEO}"
        )

        if aes_key is None or iv_key is None or not segments_lst:
            _LOGGER.debug("Can't download video file %s", file_name)
            return

        if len(segments_lst) == 1:
            await self._get_file(segments_lst[0], aes_key, file_name)
            return

        # Download segments in parallel
        tasks = [
            self._get_file(segment, aes_key, f"{index}_{file_name}")
            for index, segment in enumerate(segments_lst, start=1)
        ]
        results = await asyncio.gather(*tasks)

        # Collect successful downloads
        segment_files = [
            await self.get_fpath(f"{index + 1}_{file_name}")
            for index, success in enumerate(results)
            if success
        ]

        if not segment_files:
            _LOGGER.warning("No segment files found")
        elif len(segment_files) == 1:
            _LOGGER.debug("Single file segment, no need to concatenate")
        elif len(segment_files) > 1:
            _LOGGER.debug("Concatenating video with %s segments", len(segment_files))
            await self._concat_segments(segment_files, file_name)

    async def _get_m3u8_segments(self) -> tuple[Any, str | None, list[str | None]]:
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
            _LOGGER.debug("Missing mediaApi in video data")
            raise ValueError("Missing mediaApi in video data")
        return await self.client.extract_segments_m3u8(str(media_api))

    async def _get_file(
        self, url: str | None, aes_key: str | None, full_filename: str | None
    ) -> bool:
        """Download a file from a URL and decrypt it.
        :param url: URL of the file to download.
        :param aes_key: AES key used for decryption.
        :param full_filename: Name of the file to save.
        :return: True if the file was downloaded successfully, False otherwise.
        """
        if not url or not aes_key or not full_filename:
            _LOGGER.debug("Missing URL, AES key, or filename")
            return False

        # Download the file
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                _LOGGER.error(
                    "Failed to download %s, status code: %s", url, response.status
                )
                return False

            encrypted_data = await response.read()
        decrypted_data = await self._decrypt_data(encrypted_data, aes_key)

        if decrypted_data:
            _LOGGER.debug("Decrypt was successful")
            await self._save_file(decrypted_data, full_filename)
            return True
        return False

    async def _save_file(self, content: bytes, filename: str) -> Path:
        """Save content to a file asynchronously and return the file path.
        :param content: Bytes data to save.
        :param filename: Name of the file to save.
        :return: Path of the saved file.
        """
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
    async def _decrypt_data(encrypted_data: bytes, aes_key: str) -> bytes | None:
        """Decrypt a file using AES encryption.
        :param encrypted_data: Encrypted bytes data.
        :param aes_key: AES key used for decryption.
        :return: Decrypted bytes data.
        """
        aes_key = aes_key.removesuffix("\n")
        key_bytes: bytes = aes_key.encode("utf-8")
        iv: bytes = b"\x61" * 16
        cipher: Any = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_data: bytes = cipher.decrypt(encrypted_data)

        try:
            decrypted_data = unpad(decrypted_data, AES.block_size)
        except ValueError as e:
            _LOGGER.debug("Ignoring unpad warning : %s", e)
        return decrypted_data

    async def _concat_segments(self, ts_files: list[Path], output_file) -> None:
        """Concatenate a list of .mp4 segments into a single output file without using a temporary file.

        :param ts_files: List of absolute paths of .mp4 files
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

    @staticmethod
    async def _delete_segments(ts_files: list[Path]) -> None:
        """Delete all segment files after concatenation.
        :param ts_files: List of absolute paths of .mp4 files
        """
        for file in ts_files:
            if file.exists():
                try:
                    file.unlink()
                    _LOGGER.debug("Deleted segment file: %s", file)
                except OSError as e:
                    _LOGGER.debug("Error deleting segment file %s: %s", file, e)
            else:
                _LOGGER.debug("Segment file not found: %s", file)
