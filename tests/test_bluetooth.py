import unittest
from unittest.mock import AsyncMock, patch
from pypetkitapi.bluetooth import BluetoothManager
from pypetkitapi import PetKitClient


class TestBluetoothManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = AsyncMock(spec=PetKitClient)
        self.bluetooth_manager = BluetoothManager(self.client)

    @patch(
        "pypetkitapi.bluetooth.BluetoothManager._encode_ble_data",
        new_callable=AsyncMock,
    )
    async def test_get_ble_cmd_data(self, mock_encode_ble_data):
        # Mock the encoded data
        mock_encode_ble_data.return_value = "encoded_data"

        fountain_command = [1, 2, 3, 4]
        counter = 5
        expected_cmd_code = 1
        expected_ble_data = [0xAA, 0xBB, 1, 2, 5, 3, 4, 0xCC, 0xDD]  # Example values
        expected_encoded_data = "encoded_data"

        with patch("pypetkitapi.bluetooth.BLE_START_TRAME", [0xAA, 0xBB]), patch(
            "pypetkitapi.bluetooth.BLE_END_TRAME", [0xCC, 0xDD]
        ):
            cmd_code, encoded_data = await self.bluetooth_manager.get_ble_cmd_data(
                fountain_command, counter
            )

        self.assertEqual(cmd_code, expected_cmd_code)
        self.assertEqual(encoded_data, expected_encoded_data)
        mock_encode_ble_data.assert_called_once_with(expected_ble_data)


if __name__ == "__main__":
    unittest.main()
