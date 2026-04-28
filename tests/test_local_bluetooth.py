"""Tests for pypetkitapi.local_bluetooth.LocalFountainBleProtocol."""

from __future__ import annotations

import unittest

from pypetkitapi.local_bluetooth import (
    BLE_FOUNTAIN_NAME_PREFIXES,
    BLE_NOTIFY_UUID,
    BLE_WRITE_UUID,
    LocalFountainBleProtocol,
)


def _frame(cmd: int, cmd_type: int, seq: int, data: list[int]) -> bytearray:
    """Helper: build a raw BLE frame for tests (mirrors build_command)."""
    return bytearray(
        [0xFA, 0xFC, 0xFD, cmd, cmd_type, seq, len(data), 0, *data, 0xFB]
    )


class TestConstants(unittest.TestCase):
    def test_ble_uuids_are_petkit_fountain(self):
        self.assertEqual(BLE_WRITE_UUID, "0000aaa2-0000-1000-8000-00805f9b34fb")
        self.assertEqual(BLE_NOTIFY_UUID, "0000aaa1-0000-1000-8000-00805f9b34fb")

    def test_name_prefixes_cover_known_fountains(self):
        self.assertIn("Petkit_W4", BLE_FOUNTAIN_NAME_PREFIXES)
        self.assertIn("Petkit_W5", BLE_FOUNTAIN_NAME_PREFIXES)
        self.assertIn("Petkit_CTW", BLE_FOUNTAIN_NAME_PREFIXES)


class TestCommandFraming(unittest.TestCase):
    def setUp(self) -> None:
        self.proto = LocalFountainBleProtocol()

    def test_build_command_layout(self):
        frame = self.proto.build_command(213, 1, [0, 0])
        # Header
        self.assertEqual(list(frame[:3]), [0xFA, 0xFC, 0xFD])
        # cmd / type / seq / len / 0
        self.assertEqual(frame[3], 213)
        self.assertEqual(frame[4], 1)
        self.assertEqual(frame[5], 0)
        self.assertEqual(frame[6], 2)
        self.assertEqual(frame[7], 0)
        # payload + end byte
        self.assertEqual(list(frame[8:10]), [0, 0])
        self.assertEqual(frame[-1], 0xFB)

    def test_sequence_increments(self):
        self.proto.build_command(213, 1, [0, 0])
        second = self.proto.build_command(213, 1, [0, 0])
        self.assertEqual(second[5], 1)

    def test_sequence_wraps_at_256(self):
        # Sequence is 0..255 then wraps. After 257 calls the last seq used is 0.
        for _ in range(257):
            frame = self.proto.build_command(213, 1, [0, 0])
        self.assertEqual(frame[5], 0)

    def test_get_init_commands_returns_only_device_id_request(self):
        cmds = self.proto.get_init_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0][3], LocalFountainBleProtocol.CMD_DEVICE_ID)

    def test_complete_init_returns_empty_without_device_id(self):
        self.assertEqual(self.proto.complete_init_commands(), [])

    def test_get_status_command(self):
        frame = self.proto.get_status_command()
        self.assertEqual(frame[3], LocalFountainBleProtocol.CMD_FULL_STATUS)
        self.assertEqual(frame[4], 2)
        self.assertEqual(list(frame[8:9]), [1])


class TestSetModeCommand(unittest.TestCase):
    """The third payload byte's interpretation is device-specific.

    See the docstring of ``build_set_mode_command`` for the underlying
    regression (PR Jezza34000/homeassistant_petkit#203).
    """

    def test_ctw3_sends_apply_byte_one(self):
        proto = LocalFountainBleProtocol("CTW3")
        frame = proto.build_set_mode_command(1, 2)
        self.assertEqual(list(frame[8:11]), [1, 2, 1])

    def test_ctw3_lowercase_alias_is_normalized(self):
        proto = LocalFountainBleProtocol("ctw3")
        frame = proto.build_set_mode_command(1, 2)
        self.assertEqual(list(frame[8:11]), [1, 2, 1])

    def test_generic_w5_sends_zero_to_avoid_pause_flag(self):
        proto = LocalFountainBleProtocol("W5")
        frame = proto.build_set_mode_command(1, 2)
        self.assertEqual(list(frame[8:11]), [1, 2, 0])

    def test_ctw2_sends_zero_to_avoid_pause_flag(self):
        proto = LocalFountainBleProtocol("CTW2")
        frame = proto.build_set_mode_command(1, 2)
        self.assertEqual(list(frame[8:11]), [1, 2, 0])

    def test_standard_to_intermittent_and_back_are_symmetric(self):
        proto = LocalFountainBleProtocol("CTW2")
        std_to_int = proto.build_set_mode_command(1, 2)
        int_to_std = proto.build_set_mode_command(1, 1)
        # Both transitions should use the same suspend byte (0)
        self.assertEqual(std_to_int[10], int_to_std[10])
        self.assertEqual(std_to_int[10], 0)


class TestNotificationParsing(unittest.TestCase):
    def test_handle_notification_accepts_bytes(self):
        proto = LocalFountainBleProtocol()
        # Device ID response, payload of 8 bytes (alias prefix 2 + id 6)
        payload = [0xAA, 0xBB, 1, 2, 3, 4, 5, 6]
        frame = bytes(_frame(LocalFountainBleProtocol.CMD_DEVICE_ID, 1, 0, payload))
        self.assertIsNone(proto.handle_notification(frame))
        self.assertTrue(proto.device_id_received)

    def test_handle_notification_accepts_memoryview(self):
        proto = LocalFountainBleProtocol()
        payload = [0xAA, 0xBB, 1, 2, 3, 4, 5, 6]
        frame = memoryview(
            bytes(_frame(LocalFountainBleProtocol.CMD_DEVICE_ID, 1, 0, payload))
        )
        self.assertIsNone(proto.handle_notification(frame))
        self.assertTrue(proto.device_id_received)

    def test_complete_init_after_device_id_returns_three_commands(self):
        proto = LocalFountainBleProtocol()
        payload = [0xAA, 0xBB, 1, 2, 3, 4, 5, 6]
        proto.handle_notification(_frame(213, 1, 0, payload))
        cmds = proto.complete_init_commands()
        self.assertEqual(len(cmds), 3)
        cmd_codes = [c[3] for c in cmds]
        self.assertEqual(
            cmd_codes,
            [
                LocalFountainBleProtocol.CMD_INIT,
                LocalFountainBleProtocol.CMD_SYNC,
                LocalFountainBleProtocol.CMD_SET_DATETIME,
            ],
        )

    def test_handle_notification_rejects_short_frame(self):
        proto = LocalFountainBleProtocol()
        self.assertIsNone(proto.handle_notification(b"\xfa\xfc\xfd"))

    def test_handle_notification_rejects_bad_header(self):
        proto = LocalFountainBleProtocol()
        bad = bytes([0x00, 0x00, 0x00, 213, 1, 0, 0, 0, 0xFB])
        self.assertIsNone(proto.handle_notification(bad))

    def test_handle_notification_rejects_bad_end_byte(self):
        proto = LocalFountainBleProtocol()
        bad = bytes([0xFA, 0xFC, 0xFD, 213, 1, 0, 0, 0, 0x00])
        self.assertIsNone(proto.handle_notification(bad))


class TestStateParsingGenericGuards(unittest.TestCase):
    def test_generic_state_truncated_returns_empty_dict(self):
        """Regression: generic _parse_state previously raised IndexError on short frames."""
        proto = LocalFountainBleProtocol("W5")
        # Send a too-short state notification (5 bytes payload, needs >=12)
        frame = _frame(LocalFountainBleProtocol.CMD_DEVICE_STATE, 1, 0, [1, 1, 0, 0, 0])
        # Should not raise
        result = proto.handle_notification(frame)
        self.assertEqual(result, {})

    def test_generic_state_full_payload_parses(self):
        proto = LocalFountainBleProtocol("W5")
        payload = [
            1,  # power_status
            2,  # mode
            0,  # dnd
            0,  # warning_breakdown
            0,  # warning_water_missing
            0,  # warning_filter
            0, 0, 0, 60,  # pump_runtime (big-endian)
            50,  # filter_percentage raw
            1,  # running_status
        ]
        frame = _frame(LocalFountainBleProtocol.CMD_DEVICE_STATE, 1, 0, payload)
        result = proto.handle_notification(frame)
        assert result is not None
        self.assertEqual(result["mode"], 2)
        self.assertEqual(result["pump_runtime"], 60)
        self.assertAlmostEqual(result["filter_percentage"], 0.5)
        self.assertEqual(result["running_status"], 1)

    def test_ctw3_alias_case_insensitive_routing(self):
        """Regression: CTW3 layout was only picked when alias matched 'CTW3' uppercase."""
        for alias in ("CTW3", "ctw3", "Ctw3"):
            proto = LocalFountainBleProtocol(alias)
            # Build a 26-byte CTW3 state payload
            payload = [0] * 26
            payload[2] = 7  # mode (any sentinel value)
            frame = _frame(LocalFountainBleProtocol.CMD_DEVICE_STATE, 1, 0, payload)
            result = proto.handle_notification(frame)
            assert result is not None, alias
            self.assertIn("suspend_status", result, alias)
            self.assertEqual(result["mode"], 7, alias)


class TestCalculateValues(unittest.TestCase):
    def test_energy_uses_today_runtime_and_returns_float(self):
        days, water_total, water_today, energy = (
            LocalFountainBleProtocol._calculate_values(
                mode=1,
                filter_pct=1.0,
                smart_time_on=0,
                smart_time_off=0,
                alias="W5",
                pump_runtime_today=3_600_000,  # 1 kWh-equivalent at 1.0 power_coeff
                pump_runtime=10_000_000,  # lifetime; must NOT show up in energy
            )
        )
        self.assertIsInstance(energy, float)
        # 0.75 power_coeff * 3_600_000 / 3_600_000 = 0.75
        self.assertAlmostEqual(energy, 0.75)
        self.assertIsInstance(water_total, int)
        self.assertIsInstance(water_today, int)
        self.assertIsInstance(days, int)

    def test_water_fields_are_int(self):
        _, water_total, water_today, _ = LocalFountainBleProtocol._calculate_values(
            mode=2,
            filter_pct=0.5,
            smart_time_on=10,
            smart_time_off=20,
            alias="ctw3",
            pump_runtime_today=120,
            pump_runtime=600,
        )
        self.assertIsInstance(water_total, int)
        self.assertIsInstance(water_today, int)


if __name__ == "__main__":
    unittest.main()
