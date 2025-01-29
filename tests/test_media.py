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
    DownloadDecryptMedia,
    MediaCloud,
)
from pypetkitapi.containers import CloudProduct


class TestMediaManager(unittest.IsolatedAsyncioTestCase):
    """Test MediaManager class"""

    def setUp(self):
        """Set up test environment"""
        self.media_manager = MediaManager()
        self.download_path = Path("/mock/download/path")
        self.client = AsyncMock(spec=PetKitClient)
        self.dl_decrypt_media = DownloadDecryptMedia(self.download_path, self.client)
        self.dl_decrypt_media.file_data = MediaCloud(
            event_id="event_001",
            event_type=RecordType.EAT,
            device_id=123,
            user_id=456,
            image="http://example.com/image.jpg",
            video="http://example.com/video.mp4",
            filepath="123/20230101/eat",
            aes_key="test_key",
            timestamp=1672531200,
        )

    @patch("pypetkitapi.media.MediaManager._get_timestamp", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.get_date_from_ts", new_callable=AsyncMock)
    @patch("pypetkitapi.media.MediaManager.construct_video_url", new_callable=AsyncMock)
    async def test_process_feeder(
        self, mock_construct_video_url, mock_get_date_from_ts, mock_get_timestamp
    ):
        """Test _process_feeder method"""
        # Mock Feeder device
        feeder = MagicMock(spec=Feeder)
        feeder.device_nfo = MagicMock()
        feeder.device_nfo.device_id = 123
        feeder.device_nfo.device_type = "FEEDER_WITH_CAMERA_TYPE"
        feeder.user = MagicMock()
        feeder.user.id = 456
        feeder.name = "Test Feeder"
        feeder.device_records = MagicMock()
        feeder.cloud_product = MagicMock(spec=CloudProduct)
        feeder.cloud_product.work_indate = 1672531200  # Mock work_indate

        # Mock record item
        record_item = MagicMock(spec=RecordsItems)
        record_item.event_id = "event_001"
        record_item.aes_key = "test_key"
        record_item.preview = "http://example.com/image.jpg"
        record_item.timestamp = 1672531200  # 2023-01-01
        record_item.media_api = "http://example.com/media_api"

        # Mock records
        feeder.device_records.eat = [MagicMock(items=[record_item])]

        # Mock return values
        mock_get_timestamp.return_value = 1672531200
        mock_get_date_from_ts.return_value = "20230101"
        mock_construct_video_url.return_value = "http://example.com/video.mp4"

        media_files = await self.media_manager._process_feeder(feeder)

        self.assertEqual(len(media_files), 1)
        self.assertEqual(media_files[0].event_id, "event_001")
        self.assertEqual(media_files[0].event_type, RecordType.EAT)
        self.assertEqual(media_files[0].device_id, 123)
        self.assertEqual(media_files[0].user_id, 456)
        self.assertEqual(media_files[0].image, "http://example.com/image.jpg")
        self.assertEqual(media_files[0].video, "http://example.com/video.mp4")
        self.assertEqual(media_files[0].filepath, "123/20230101/eat")
        self.assertEqual(media_files[0].aes_key, "test_key")
        self.assertEqual(media_files[0].timestamp, 1672531200)

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
        litter.device_nfo.device_id = 789
        litter.device_nfo.device_type = "LITTER_WITH_CAMERA_TYPE"
        litter.user = MagicMock()
        litter.user.id = 101112
        litter.name = "Test Litter"
        litter.cloud_product = MagicMock()
        litter.cloud_product.work_indate = 1672531200  # Mock work_indate

        # Mock record item
        record_item = MagicMock(spec=LitterRecord)
        record_item.event_id = "event_002"
        record_item.aes_key = "test_key"
        record_item.preview = "http://example.com/image.jpg"
        record_item.timestamp = 1672531200  # 2023-01-01
        record_item.media_api = "http://example.com/media_api"

        # Mock records
        litter.device_records = [record_item]

        # Mock return values
        mock_get_timestamp.return_value = 1672531200
        mock_get_date_from_ts.return_value = "20230101"
        mock_construct_video_url.return_value = "http://example.com/video.mp4"

        media_files = await self.media_manager._process_litter(litter)

        self.assertEqual(len(media_files), 1)
        self.assertEqual(media_files[0].event_id, "event_002")
        self.assertEqual(media_files[0].event_type, RecordType.TOILETING)
        self.assertEqual(media_files[0].device_id, 789)
        self.assertEqual(media_files[0].user_id, 101112)
        self.assertEqual(media_files[0].image, "http://example.com/image.jpg")
        self.assertEqual(media_files[0].video, "http://example.com/video.mp4")
        self.assertEqual(media_files[0].filepath, "789/20230101/toileting")
        self.assertEqual(media_files[0].aes_key, "test_key")
        self.assertEqual(media_files[0].timestamp, 1672531200)

    async def test_get_timestamp(self):
        """Test _get_timestamp method"""
        media_manager = MediaManager()

        # Create a mock item with various timestamp attributes
        item = MagicMock()
        item.timestamp = 1672531200
        item.completed_at = None
        item.eat_start_time = None
        item.eat_end_time = None
        item.start_time = None
        item.end_time = None
        item.time = None

        # Test when timestamp is present
        timestamp = await media_manager._get_timestamp(item)
        self.assertEqual(timestamp, 1672531200)

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
        media_url = (
            "http://example.com/media?startTime=1234567890&deviceId=123&mark=abc"
        )
        user_id = 456
        cp_sub = True

        expected_url = (
            "/feeder/cloud/video?startTime=1234567890&deviceId=123&userId=456&mark=abc"
        )
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
        timestamp = 1672531200  # Corresponds to 2023-01-01
        expected_date = "20230101"
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

    async def test_get_fpath_image(self):
        """Test get_fpath method when the file name is an image"""
        file_name = "test_image.jpg"
        expected_path = self.download_path / "123/20230101/eat/snapshot/test_image.jpg"
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertEqual(result, expected_path)

    async def test_get_fpath_video(self):
        """Test get_fpath method when the file name is a video"""
        file_name = "test_video.mp4"
        expected_path = self.download_path / "123/20230101/eat/video/test_video.mp4"
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertEqual(result, expected_path)

    async def test_get_fpath_failed(self):
        """Test get_fpath method when the file name is not found"""
        file_name = "test_video.mp4"
        expected_path = self.download_path / "123/test_video.mp4"
        result = await self.dl_decrypt_media.get_fpath(file_name)
        self.assertFalse(result == expected_path)


if __name__ == "__main__":
    unittest.main()
