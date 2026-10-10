import unittest
from unittest.mock import AsyncMock, patch
from pypetkitapi.bluetooth import BluetoothManager
from pypetkitapi import PetKitClient
from pypetkitapi.command import FountainAction


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

    async def _sent_command(self, action, mode, device_type="w5"):
        device_nfo = type("D", (), {"device_type": device_type})()
        fountain = type(
            "F", (), {"mode": mode, "ble_counter": 0, "device_nfo": device_nfo}
        )()
        bm = self.bluetooth_manager
        with patch.object(
            bm, "_get_fountain_instance", AsyncMock(return_value=fountain)
        ), patch.object(
            bm, "open_ble_connection", AsyncMock(return_value=True)
        ), patch.object(
            bm, "_request_ble_api", AsyncMock(return_value=1)
        ), patch.object(
            bm, "get_ble_cmd_data", AsyncMock(return_value=(220, "x"))
        ) as cmd_data:
            self.assertTrue(await bm.send_ble_command(1, action))
        return cmd_data.call_args.args[0]

    async def test_pause_and_resume_keep_current_mode(self):
        # the app sends [power, mode] and keeps the fountain's mode
        self.assertEqual(
            await self._sent_command(FountainAction.PAUSE, 2), [220, 1, 2, 0, 0, 2]
        )
        self.assertEqual(
            await self._sent_command(FountainAction.CONTINUE, 2),
            [220, 1, 2, 0, 1, 2],
        )
        self.assertEqual(
            await self._sent_command(FountainAction.CONTINUE, 1),
            [220, 1, 2, 0, 1, 1],
        )

    async def test_resume_without_known_mode_uses_normal(self):
        self.assertEqual(
            await self._sent_command(FountainAction.CONTINUE, None),
            [220, 1, 2, 0, 1, 1],
        )

    async def test_mode_commands(self):
        self.assertEqual(
            await self._sent_command(FountainAction.MODE_SMART, 1),
            [220, 1, 2, 0, 1, 2],
        )
        self.assertEqual(
            await self._sent_command(FountainAction.MODE_NORMAL, 2),
            [220, 1, 2, 0, 1, 1],
        )

    async def test_ctw3_keeps_three_byte_payload(self):
        # CTW3 uses [power, suspend, mode]; only the W5 gets the short payload
        self.assertEqual(
            await self._sent_command(FountainAction.PAUSE, 1, "ctw3"),
            [220, 1, 3, 0, 1, 0, 2],
        )
        self.assertEqual(
            await self._sent_command(FountainAction.CONTINUE, 1, "ctw3"),
            [220, 1, 3, 0, 1, 1, 2],
        )
        self.assertEqual(
            await self._sent_command(FountainAction.POWER_OFF, 2, "ctw3"),
            [220, 1, 3, 0, 0, 1, 1],
        )


if __name__ == "__main__":
    unittest.main()
