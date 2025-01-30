import asyncio
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from pypetkitapi import Litter, LitterRecord, PetKitClient
from pypetkitapi.media import (
    MediaManager,
    RecordType,
    Feeder,
    RecordsItems,
    MediaCloud,
)
from pypetkitapi.containers import CloudProduct
from pypetkitapi.media import DownloadDecryptMedia


TS_WORK_INDATE = 1672531200  # 2023-01-01
DEVICE_ID = 855554752
USER_ID = 794568421
EVENT_ID_EAT = "1000768495_1738225278"
EVENT_ID_TOILETING = "200077785_1738138878"
DATE_YYYYMMDD = "20230101"
DEVICE_NAME = "Test Device"
IMG_URL = "http://example.com/image.jpg"
VIDEO_URL = "http://example.com/video.mp4"
AES_KEY = "ff0b540e65f347db"
DECRYPTED_DATA = b"WElDrhuRtStQuIHKCurwFIKjdQriKnZSZbhPlKdbXSCDjIYNHFMWTmtyzReOORRa"
ENCRYPTED_DATA = b"\xf9\xab+\x83st\x87\xcf3\xd5\x99\xe4\xba\xbd\xad4%RN\xf5\x1c\x8b\xd6\x10\x8c\xf2\xbdz<\xcc\xf7{\xd1/\xd1\xaeu\x1c\x18\x9a\x8d\xf2\xab \x88\x8e\xd4\x9b\xb7\xac\x90\x1a\xb9\xb2\xd0TrZ\xc5\x80\x02\xc6\xb3\x84\x90\x04\xfe\x9d\xa6\x8b|Y\xec\xba\x05\xd5\x98\xde\x8d\xfd"


class TestMediaManager(unittest.IsolatedAsyncioTestCase):
    """Test MediaManager class"""

    def setUp(self):
        """Set up test environment"""
        self.media_manager = MediaManager()
        self.download_path = Path("/mock/download/path")
        self.client = AsyncMock(spec=PetKitClient)
        self.dl_decrypt_media = DownloadDecryptMedia(self.download_path, self.client)
        self.dl_decrypt_media.file_data = MediaCloud(
            event_id=EVENT_ID_EAT,
            event_type=RecordType.EAT,
            device_id=DEVICE_ID,
            user_id=USER_ID,
            image=IMG_URL,
            video=VIDEO_URL,
            filepath=f"{DEVICE_ID}/{DATE_YYYYMMDD}/{RecordType.EAT}",
            aes_key=AES_KEY,
            timestamp=TS_WORK_INDATE,
        )
        # Mock Feeder device
        feeder = MagicMock(spec=Feeder)
        feeder.device_nfo = MagicMock()
        feeder.device_nfo.device_id = DEVICE_ID
        feeder.device_nfo.device_type = "FEEDER"
        feeder.user = MagicMock()
        feeder.user.id = USER_ID
        feeder.name = DEVICE_NAME
        feeder.device_records = MagicMock()
        feeder.cloud_product = MagicMock(spec=CloudProduct)
        feeder.cloud_product.work_indate = TS_WORK_INDATE
        # Mock record item
        record_item = MagicMock(spec=RecordsItems)
        record_item.event_id = EVENT_ID_EAT
        record_item.aes_key = AES_KEY
        record_item.preview = IMG_URL
        record_item.timestamp = TS_WORK_INDATE
        record_item.media_api = "http://example.com/media_api"
        # Mock records
        feeder.device_records.eat = [MagicMock(items=[record_item])]
        self.feeder = feeder

    async def test_process_feeder_no_records(self):
        """Test _process_feeder method"""
        self.feeder.device_records = None
        result = await self.media_manager._process_feeder(self.feeder)
        self.assertEqual(result, [])

    @patch("pypetkitapi.media.MediaManager._get_timestamp", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.get_date_from_ts", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.construct_video_url", new_callable=AsyncMock)
    async def test_process_feeder(
        self, mock_construct_video_url, mock_get_date_from_ts, mock_get_timestamp
    ):
        """Test _process_feeder method"""

        # Mock return values
        mock_get_timestamp.return_value = TS_WORK_INDATE
        mock_get_date_from_ts.return_value = DATE_YYYYMMDD
        mock_construct_video_url.return_value = VIDEO_URL

        media_files = await self.media_manager._process_feeder(self.feeder)

        self.assertEqual(len(media_files), 1)
        self.assertEqual(media_files[0].event_id, EVENT_ID_EAT)
        self.assertEqual(media_files[0].event_type, RecordType.EAT)
        self.assertEqual(media_files[0].device_id, DEVICE_ID)
        self.assertEqual(media_files[0].user_id, USER_ID)
        self.assertEqual(media_files[0].image, IMG_URL)
        self.assertEqual(media_files[0].video, VIDEO_URL)
        self.assertEqual(
            media_files[0].filepath, f"{DEVICE_ID}/{DATE_YYYYMMDD}/{RecordType.EAT}"
        )
        self.assertEqual(media_files[0].aes_key, AES_KEY)
        self.assertEqual(media_files[0].timestamp, TS_WORK_INDATE)

    async def test_process_feeder_missing_records_data(self):
        """Test _process_feeder method"""

        # Test no user ID
        self.feeder.user.id = None
        media_files = await self.media_manager._process_feeder(self.feeder)
        self.assertEqual(len(media_files), 0)

        # Test no aes_key
        self.feeder.user.id = USER_ID
        self.feeder.device_records.eat[0].items[0].aes_key = None
        media_files = await self.media_manager._process_feeder(self.feeder)
        self.assertEqual(len(media_files), 0)

        # Test no item id
        self.feeder.device_records.eat[0].items[0].aes_key = AES_KEY
        self.feeder.device_records.eat[0].items[0].event_id = None
        media_files = await self.media_manager._process_feeder(self.feeder)
        self.assertEqual(len(media_files), 0)

    @patch("pypetkitapi.media.MediaManager._get_timestamp", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.get_date_from_ts", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.construct_video_url", new_callable=AsyncMock)
    async def test_process_litter(
        self, mock_construct_video_url, mock_get_date_from_ts, mock_get_timestamp
    ):
        """Test _process_litter method"""
        # Mock Litter device
        litter = MagicMock(spec=Litter)
        litter.device_nfo = MagicMock()
        litter.device_nfo.device_id = DEVICE_ID
        litter.device_nfo.device_type = "LITTER"
        litter.user = MagicMock()
        litter.user.id = USER_ID
        litter.name = DEVICE_NAME
        litter.cloud_product = MagicMock()
        litter.cloud_product.work_indate = TS_WORK_INDATE

        # Mock record item
        record_item = MagicMock(spec=LitterRecord)
        record_item.event_id = EVENT_ID_TOILETING
        record_item.aes_key = AES_KEY
        record_item.preview = IMG_URL
        record_item.timestamp = TS_WORK_INDATE
        record_item.media_api = "http://example.com/media_api"

        # Mock records
        litter.device_records = [record_item]

        # Mock return values
        mock_get_timestamp.return_value = TS_WORK_INDATE
        mock_get_date_from_ts.return_value = DATE_YYYYMMDD
        mock_construct_video_url.return_value = VIDEO_URL

        media_files = await self.media_manager._process_litter(litter)

        self.assertEqual(len(media_files), 1)
        self.assertEqual(media_files[0].event_id, EVENT_ID_TOILETING)
        self.assertEqual(media_files[0].event_type, RecordType.TOILETING)
        self.assertEqual(media_files[0].device_id, DEVICE_ID)
        self.assertEqual(media_files[0].user_id, USER_ID)
        self.assertEqual(media_files[0].image, IMG_URL)
        self.assertEqual(media_files[0].video, VIDEO_URL)
        self.assertEqual(
            media_files[0].filepath,
            f"{DEVICE_ID}/{DATE_YYYYMMDD}/{RecordType.TOILETING}",
        )
        self.assertEqual(media_files[0].aes_key, AES_KEY)
        self.assertEqual(media_files[0].timestamp, TS_WORK_INDATE)

    async def test_get_timestamp(self):
        """Test _get_timestamp method"""
        media_manager = MediaManager()

        # Create a mock item with various timestamp attributes
        item = MagicMock()
        item.timestamp = TS_WORK_INDATE
        item.completed_at = None
        item.eat_start_time = None
        item.eat_end_time = None
        item.start_time = None
        item.end_time = None
        item.time = None

        # Test when timestamp is present
        timestamp = await media_manager._get_timestamp(item)
        self.assertEqual(timestamp, TS_WORK_INDATE)

        # Test when timestamp is None but completed_at is present
        item.timestamp = None
        item.completed_at = 1672531300
        timestamp = await media_manager._get_timestamp(item)
        self.assertEqual(timestamp, 1672531300)

        # Test when all attributes are None
        item.completed_at = None
        timestamp = await media_manager._get_timestamp(item)
        self.assertIsNone(timestamp)

    async def test_construct_video_url(self):
        """Test construct_video_url method"""
        device_type = "feeder"
        media_url = f"http://example.com/media?startTime=1234567890&deviceId={DEVICE_ID}&mark=1234567890"
        user_id = USER_ID
        cp_sub = True

        expected_url = f"/feeder/cloud/video?startTime=1234567890&deviceId={DEVICE_ID}&userId={USER_ID}&mark=1234567890"
        result = await MediaManager.construct_video_url(
            device_type, media_url, user_id, cp_sub
        )
        self.assertEqual(result, expected_url)

        # Test with missing media_url
        result = await MediaManager.construct_video_url(
            device_type, None, user_id, cp_sub
        )
        self.assertIsNone(result)

        # Test with missing user_id
        result = await MediaManager.construct_video_url(
            device_type, media_url, None, cp_sub
        )
        self.assertIsNone(result)

        # Test with missing cp_sub
        result = await MediaManager.construct_video_url(
            device_type, media_url, user_id, None
        )
        self.assertIsNone(result)

    async def test_get_date_from_ts(self):
        """Test get_date_from_ts method"""
        # Test with a valid timestamp
        timestamp = TS_WORK_INDATE
        expected_date = DATE_YYYYMMDD
        result = await MediaManager.get_date_from_ts(timestamp)
        self.assertEqual(result, expected_date)

        # Test with None timestamp
        timestamp = None
        expected_date = "unknown"
        result = await MediaManager.get_date_from_ts(timestamp)
        self.assertEqual(result, expected_date)

    def test_is_subscription_active(self):
        """Test is_subscription_active method"""
        # Create a MediaManager instance
        media_manager = MediaManager()

        # Mock Feeder device with active subscription
        feeder = MagicMock(spec=Feeder)
        feeder.cloud_product = MagicMock(spec=CloudProduct)
        feeder.cloud_product.work_indate = int(
            (datetime.now() + timedelta(days=1)).timestamp()
        )
        self.assertTrue(media_manager.is_subscription_active(feeder))

        # Mock Feeder device with expired subscription
        feeder.cloud_product.work_indate = int(
            (datetime.now() - timedelta(days=1)).timestamp()
        )
        self.assertFalse(media_manager.is_subscription_active(feeder))

        # Mock Litter device with active subscription
        litter = MagicMock(spec=Litter)
        litter.cloud_product = MagicMock(spec=CloudProduct)
        litter.cloud_product.work_indate = int(
            (datetime.now() + timedelta(days=1)).timestamp()
        )
        self.assertTrue(media_manager.is_subscription_active(litter))

        # Mock Litter device with expired subscription
        litter.cloud_product.work_indate = int(
            (datetime.now() - timedelta(days=1)).timestamp()
        )
        self.assertFalse(media_manager.is_subscription_active(litter))

        # Test with no cloud_product
        feeder.cloud_product = None
        self.assertFalse(media_manager.is_subscription_active(feeder))

    @patch("pypetkitapi.media.DownloadDecryptMedia.get_fpath", new_callable=AsyncMock)
    async def test_not_existing_file(self, mock_get_fpath):
        """Test not_existing_file method"""
        # Mock the file path
        mock_file_path = AsyncMock(spec=Path)
        mock_get_fpath.return_value = mock_file_path

        # Test when file exists
        mock_file_path.exists.return_value = True
        result = await self.dl_decrypt_media.not_existing_file("test_file.jpg")
        self.assertFalse(result)
        mock_file_path.exists.assert_called_once()

        # Test when file does not exist
        mock_file_path.exists.return_value = False
        result = await self.dl_decrypt_media.not_existing_file("test_file.jpg")
        self.assertTrue(result)
        self.assertEqual(mock_file_path.exists.call_count, 2)

    @patch("pypetkitapi.media.DownloadDecryptMedia.get_fpath", new_callable=AsyncMock)
    @patch("pypetkitapi.media.Path.exists", new_callable=MagicMock)
    async def test_concat_segments_output_exists(self, mock_exists, mock_get_fpath):
        # Mock the paths
        mock_ts_files = [MagicMock(spec=Path) for _ in range(3)]
        mock_output_file = MagicMock(spec=Path)
        mock_get_fpath.side_effect = [mock_output_file] + mock_ts_files

        # Mock the existence of the output file
        mock_exists.side_effect = [True] + [False] * 3

        # Call the method
        await self.dl_decrypt_media._concat_segments(mock_ts_files, "output.mp4")

        # Assertions
        mock_get_fpath.assert_called()
        for mock_ts_file in mock_ts_files:
            mock_ts_file.unlink.assert_called_once()

    async def test_get_fpath_image(self):
        """Test get_fpath method when the file name is an image"""
        file_name = "test_image.jpg"
        expected_path = (
            self.download_path
            / f"{DEVICE_ID}/{DATE_YYYYMMDD}/{RecordType.EAT}/snapshot/test_image.jpg"
        )
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertEqual(result, expected_path)

    async def test_get_fpath_video(self):
        """Test get_fpath method when the file name is a video"""
        file_name = "test_video.mp4"
        expected_path = (
            self.download_path
            / f"{DEVICE_ID}/{DATE_YYYYMMDD}/{RecordType.EAT}/video/test_video.mp4"
        )
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertEqual(result, expected_path)

    async def test_get_fpath_failed(self):
        """Test get_fpath method when the file name is not found"""
        file_name = "test_video.mp4"
        expected_path = self.download_path / f"{DEVICE_ID}/test_video.mp4"
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertNotEqual(result, expected_path)

    async def test_delete_segments(self):
        """Test _delete_segments method"""
        mock_paths = [MagicMock(spec=Path) for _ in range(3)]
        for mock_path in mock_paths:
            mock_path.exists.return_value = True
        await DownloadDecryptMedia._delete_segments(mock_paths)

        for mock_path in mock_paths:
            mock_path.unlink.assert_called_once()

    async def test_delete_segments_file_not_found(self):
        """Test _delete_segments method when file is not found"""
        mock_paths = [MagicMock(spec=Path) for _ in range(3)]
        for mock_path in mock_paths:
            mock_path.exists.return_value = False
        await DownloadDecryptMedia._delete_segments(mock_paths)
        for mock_path in mock_paths:
            mock_path.unlink.assert_not_called()

    @patch("pypetkitapi.media.aiohttp.ClientSession.get")
    @patch(
        "pypetkitapi.media.DownloadDecryptMedia._decrypt_data", new_callable=AsyncMock
    )
    @patch("pypetkitapi.media.DownloadDecryptMedia._save_file", new_callable=AsyncMock)
    async def test_get_file(self, mock_save_file, mock_decrypt_data, mock_get):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=ENCRYPTED_DATA)
        mock_get.return_value.__aenter__.return_value = mock_response
        mock_decrypt_data.return_value = DECRYPTED_DATA
        mock_save_file.return_value = Path("/mock/download/path/test_file.jpg")

        result = await self.dl_decrypt_media._get_file(
            "http://example.com/file", AES_KEY, "test_file.jpg"
        )

        self.assertTrue(result)
        mock_get.assert_called_once_with("http://example.com/file")
        mock_decrypt_data.assert_called_once_with(ENCRYPTED_DATA, AES_KEY)
        mock_save_file.assert_called_once_with(DECRYPTED_DATA, "test_file.jpg")

    @patch("pypetkitapi.media.aiohttp.ClientSession.get")
    async def test_get_file_download_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await self.dl_decrypt_media._get_file(
            "http://example.com/file", AES_KEY, "test_file.jpg"
        )

        self.assertFalse(result)
        mock_get.assert_called_once_with("http://example.com/file")

    async def test_decrypt_data(self):
        """Test _decrypt_data method"""
        decrypted_data = await DownloadDecryptMedia._decrypt_data(
            ENCRYPTED_DATA, AES_KEY
        )
        self.assertEqual(decrypted_data, DECRYPTED_DATA)


if __name__ == "__main__":
    unittest.main()
