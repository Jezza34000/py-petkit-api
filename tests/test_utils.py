import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfoNotFoundError

from pypetkitapi.utils import get_timezone_offset


class TestUtils(unittest.TestCase):

    @patch("pypetkitapi.utils.ZoneInfo")
    @patch("pypetkitapi.utils.datetime")
    def test_get_timezone_offset_valid(self, mock_datetime, mock_zoneinfo):
        # Mock datetime and ZoneInfo
        mock_zoneinfo.return_value = "MockedZone"
        mock_now = mock_datetime.now.return_value
        mock_now.utcoffset.return_value.total_seconds.return_value = 3600

        offset = get_timezone_offset("MockedZone")
        self.assertEqual(offset, "1.0")

    @patch("pypetkitapi.utils.ZoneInfo")
    @patch("pypetkitapi.utils.datetime")
    def test_get_timezone_offset_no_offset(self, mock_datetime, mock_zoneinfo):
        # Mock datetime and ZoneInfo
        mock_zoneinfo.return_value = "MockedZone"
        mock_now = mock_datetime.now.return_value
        mock_now.utcoffset.return_value = None

        offset = get_timezone_offset("MockedZone")
        self.assertEqual(offset, "0.0")

    @patch("pypetkitapi.utils.ZoneInfo", side_effect=ZoneInfoNotFoundError)
    def test_get_timezone_offset_invalid_zone(self, mock_zoneinfo):
        offset = get_timezone_offset("InvalidZone")
        self.assertEqual(offset, "0.0")

    @patch("pypetkitapi.utils.ZoneInfo")
    @patch("pypetkitapi.utils.datetime")
    def test_get_timezone_offset_attribute_error(self, mock_datetime, mock_zoneinfo):
        # Mock datetime and ZoneInfo
        mock_zoneinfo.return_value = "MockedZone"
        mock_datetime.now.side_effect = AttributeError

        offset = get_timezone_offset("MockedZone")
        self.assertEqual(offset, "0.0")


if __name__ == "__main__":
    unittest.main()
