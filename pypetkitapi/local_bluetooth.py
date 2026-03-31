"""Local (direct) Bluetooth protocol handler for PetKit fountains.

This module is transport-agnostic. It handles the BLE protocol
(command building, frame parsing, initialization sequence) without
depending on any specific BLE library. The caller provides a write
function and receives parsed status via handle_notification().

BLE frame format:
  Header:     [0xFA, 0xFC, 0xFD]
  Command:    [cmd, type, seq, length, 0x00]
  Data:       [...]
  End:        [0xFB]

UUIDs:
  Write:   0000aaa2-0000-1000-8000-00805f9b34fb
  Notify:  0000aaa1-0000-1000-8000-00805f9b34fb
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pypetkitapi.water_fountain_container import WaterFountain

_LOGGER = logging.getLogger(__name__)

BLE_WRITE_UUID = "0000aaa2-0000-1000-8000-00805f9b34fb"
BLE_NOTIFY_UUID = "0000aaa1-0000-1000-8000-00805f9b34fb"

BLE_FOUNTAIN_NAME_PREFIXES = ("Petkit_W4", "Petkit_W5", "Petkit_CTW")


class LocalFountainBleProtocol:
    """Transport-agnostic BLE protocol handler for PetKit fountains.

    Usage:
        1. Create an instance, optionally passing the device alias ("CTW3", "W5", ...).
        2. Call get_init_commands() to get the first command (CMD 213).
        3. Send that command via BLE and wait for the notification.
        4. Pass the notification bytes to handle_notification() — when it returns None
           with CMD_DEVICE_ID internally processed, call complete_init_commands()
           to get the remaining init commands (CMD 73, 86, 84).
        5. After init, call get_status_command() and send it.
        6. Pass notifications to handle_notification() to get the status dict.
    """

    # Command codes
    CMD_BATTERY = 66
    CMD_INIT = 73
    CMD_SET_DATETIME = 84
    CMD_SYNC = 86
    CMD_FIRMWARE = 200
    CMD_DEVICE_TYPE = 201
    CMD_DEVICE_STATE = 210
    CMD_DEVICE_CONFIG = 211
    CMD_DEVICE_ID = 213
    CMD_SET_MODE = 220
    CMD_SET_CONFIG = 221
    CMD_FULL_STATUS = 230

    _HEADER = [0xFA, 0xFC, 0xFD]
    _END_BYTE = 0xFB

    def __init__(self, device_alias: str = "") -> None:
        """Initialize the protocol handler."""
        self._sequence = 0
        self._device_id_bytes: list[int] = []
        self._secret: list[int] = []
        self.device_alias = device_alias
        self.device_id_received = False

    # -----------------------------------------------------------------------
    # Command building
    # -----------------------------------------------------------------------

    def _next_seq(self) -> int:
        seq = self._sequence
        self._sequence = (self._sequence + 1) % 256
        return seq

    def build_command(self, cmd: int, cmd_type: int, data: list[int]) -> bytearray:
        """Build a BLE command frame."""
        seq = self._next_seq()
        length = len(data)
        frame = self._HEADER + [cmd, cmd_type, seq, length, 0] + data + [self._END_BYTE]
        return bytearray(frame)

    def get_init_commands(self) -> list[bytearray]:
        """Return the first init command (CMD 213 — request device ID).

        Call complete_init_commands() after the CMD 213 notification is received.
        """
        return [self.build_command(self.CMD_DEVICE_ID, 1, [0, 0])]

    def complete_init_commands(self) -> list[bytearray]:
        """Return the remaining init commands (CMD 73, 86, 84).

        Must be called after handle_notification() has processed the CMD 213 response.
        """
        if not self._device_id_bytes:
            _LOGGER.warning("Device ID not yet received; cannot complete BLE init")
            return []

        device_id_padded = (self._device_id_bytes + [0] * 8)[:8]
        self._secret = self._derive_secret(device_id_padded)

        cmds: list[bytearray] = []

        # CMD 73: Init / authenticate
        init_data = [0, 0] + device_id_padded + self._secret
        cmds.append(self.build_command(self.CMD_INIT, 1, init_data))

        # CMD 86: Sync (uses secret)
        cmds.append(self.build_command(self.CMD_SYNC, 1, [0, 0] + self._secret))

        # CMD 84: Set device datetime (seconds since 2000-01-01 UTC)
        secs = self._seconds_since_2000()
        time_data = [
            0,
            (secs >> 24) & 0xFF,
            (secs >> 16) & 0xFF,
            (secs >> 8) & 0xFF,
            secs & 0xFF,
            13,
        ]
        cmds.append(self.build_command(self.CMD_SET_DATETIME, 1, time_data))

        return cmds

    def get_status_command(self) -> bytearray:
        """Return CMD 230 — full status request."""
        return self.build_command(self.CMD_FULL_STATUS, 2, [1])

    def build_set_mode_command(self, power_state: int, mode: int) -> bytearray:
        """Return CMD 220 — set operating mode."""
        return self.build_command(self.CMD_SET_MODE, 1, [power_state, mode, 1])

    def build_set_config_command(self, config_data: list[int]) -> bytearray:
        """Return CMD 221 — set device configuration."""
        return self.build_command(self.CMD_SET_CONFIG, 1, config_data)

    # -----------------------------------------------------------------------
    # Notification parsing
    # -----------------------------------------------------------------------

    def handle_notification(self, data: bytearray) -> dict[str, Any] | None:
        """Parse an incoming BLE notification.

        Returns a status dict for CMD 210/211/230, or None for protocol /
        info frames (CMD 213 response is handled internally).
        """
        if len(data) < 9:
            return None
        if data[0] != 0xFA or data[1] != 0xFC or data[2] != 0xFD:
            return None
        if data[-1] != self._END_BYTE:
            return None

        cmd = data[3]
        payload = list(data[8:-1])

        if cmd == self.CMD_DEVICE_ID:
            # Extract device ID bytes from identifier response (bytes 2–8 of payload)
            if len(payload) >= 8:
                self._device_id_bytes = payload[2:8]
                self.device_id_received = True
                _LOGGER.debug("BLE device ID received: %s", self._device_id_bytes)
            return None

        if cmd == self.CMD_FULL_STATUS:
            return self._parse_full_status(payload)

        if cmd == self.CMD_DEVICE_STATE:
            return self._parse_state(payload)

        if cmd == self.CMD_DEVICE_CONFIG:
            return self._parse_config(payload)

        return None

    # -----------------------------------------------------------------------
    # Parsing helpers
    # -----------------------------------------------------------------------

    def _parse_full_status(self, data: list[int]) -> dict[str, Any]:
        if self.device_alias == "CTW3":
            return self._parse_ctw3_full_status(data)
        return self._parse_generic_full_status(data)

    def _parse_state(self, data: list[int]) -> dict[str, Any]:
        if self.device_alias == "CTW3":
            if len(data) < 26:
                return {}
            return {
                "power_status": data[0],
                "suspend_status": data[1],
                "mode": data[2],
                "dnd_state": data[4],
                "warning_breakdown": data[5],
                "warning_water_missing": data[6],
                "low_battery": data[7],
                "warning_filter": data[8],
                "pump_runtime": int.from_bytes(bytes(data[9:13]), "big"),
                "filter_percentage": data[13] / 100.0,
                "running_status": data[14],
                "pump_runtime_today": int.from_bytes(bytes(data[15:19]), "big"),
                "supply_voltage": int.from_bytes(
                    bytes(data[20:22]), "big", signed=True
                ),
                "battery_voltage": int.from_bytes(
                    bytes(data[22:24]), "big", signed=True
                ),
                "battery_percentage": data[24],
            }
        return {
            "power_status": data[0],
            "mode": data[1],
            "dnd_state": data[2],
            "warning_breakdown": data[3],
            "warning_water_missing": data[4],
            "warning_filter": data[5],
            "pump_runtime": int.from_bytes(bytes(data[6:10]), "big"),
            "filter_percentage": (data[10] & 0xFF) / 100.0,
            "running_status": data[11] & 0xFF,
        }

    def _parse_config(self, data: list[int]) -> dict[str, Any]:
        if self.device_alias == "CTW3":
            if len(data) < 9:
                return {}
            return {
                "smart_time_on": data[0],
                "smart_time_off": data[1],
                "led_switch": data[6],
                "led_brightness": data[7],
                "do_not_disturb_switch": data[8],
            }
        if len(data) < 14:
            return {}
        return {
            "smart_time_on": data[0],
            "smart_time_off": data[1],
            "led_switch": data[2],
            "led_brightness": data[3],
            "do_not_disturb_switch": data[8],
            "led_light_time_on": int.from_bytes(bytes(data[4:6]), "big", signed=True),
            "led_light_time_off": int.from_bytes(bytes(data[6:8]), "big", signed=True),
            "do_not_disturb_time_on": int.from_bytes(
                bytes(data[9:11]), "big", signed=True
            ),
            "do_not_disturb_time_off": int.from_bytes(
                bytes(data[11:13]), "big", signed=True
            ),
        }

    def _parse_ctw3_full_status(self, data: list[int]) -> dict[str, Any]:
        if len(data) < 26:
            return {}
        mode = data[2]
        filter_pct = data[13] / 100.0
        pump_runtime = int.from_bytes(bytes(data[9:13]), "big")
        pump_runtime_today = int.from_bytes(bytes(data[15:19]), "big")
        smart_time_on = data[26] if len(data) > 26 else 0
        smart_time_off = data[27] if len(data) > 27 else 0
        filter_days, water_total, water_today, energy = self._calculate_values(
            mode,
            filter_pct,
            smart_time_on,
            smart_time_off,
            "CTW3",
            pump_runtime_today,
            pump_runtime,
        )
        return {
            "power_status": data[0],
            "suspend_status": data[1],
            "mode": mode,
            "dnd_state": data[4],
            "warning_breakdown": data[5],
            "warning_water_missing": data[6],
            "low_battery": data[7],
            "warning_filter": data[8],
            "pump_runtime": pump_runtime,
            "filter_percentage": filter_pct,
            "running_status": data[14],
            "pump_runtime_today": pump_runtime_today,
            "pet_drinking": data[19],
            "supply_voltage": int.from_bytes(bytes(data[20:22]), "big", signed=True),
            "battery_voltage": int.from_bytes(bytes(data[22:24]), "big", signed=True),
            "battery_percentage": data[24],
            "smart_time_on": smart_time_on,
            "smart_time_off": smart_time_off,
            "led_switch": data[28] if len(data) > 28 else None,
            "led_brightness": data[29] if len(data) > 29 else None,
            "do_not_disturb_switch": data[34] if len(data) > 34 else None,
            "filter_time_left": filter_days,
            "today_clean_water": water_today,
            "expected_clean_water": water_total,
            "today_use_electricity": energy,
        }

    def _parse_generic_full_status(self, data: list[int]) -> dict[str, Any]:
        if len(data) < 18:
            return {}
        mode = data[1]
        filter_pct = (data[10] & 0xFF) / 100.0
        smart_time_on = data[16]
        smart_time_off = data[17]
        pump_runtime = int.from_bytes(bytes(data[6:10]), "big")
        pump_runtime_today = int.from_bytes(bytes(data[12:16]), "big")
        filter_days, water_total, water_today, energy = self._calculate_values(
            mode,
            filter_pct,
            smart_time_on,
            smart_time_off,
            self.device_alias,
            pump_runtime_today,
            pump_runtime,
        )
        result: dict[str, Any] = {
            "power_status": data[0],
            "mode": mode,
            "dnd_state": data[2],
            "warning_breakdown": data[3],
            "warning_water_missing": data[4],
            "warning_filter": data[5],
            "pump_runtime": pump_runtime,
            "filter_percentage": filter_pct,
            "running_status": data[11] & 0xFF,
            "pump_runtime_today": pump_runtime_today,
            "smart_time_on": smart_time_on,
            "smart_time_off": smart_time_off,
            "filter_time_left": filter_days,
            "today_clean_water": water_today,
            "expected_clean_water": water_total,
            "today_use_electricity": energy,
        }
        if len(data) >= 20:
            result["led_switch"] = data[18]
            result["led_brightness"] = data[19]
        if len(data) >= 25:
            result["do_not_disturb_switch"] = data[24]
        return result

    # -----------------------------------------------------------------------
    # Water fountain entity update
    # -----------------------------------------------------------------------

    @staticmethod
    def update_water_fountain(
        fountain: WaterFountain, ble_status: dict[str, Any]
    ) -> None:
        """Apply a BLE status dict to a WaterFountain entity in-place."""
        if fountain.status is None:
            from pypetkitapi.water_fountain_container import Status

            fountain.status = Status()

        if fountain.settings is None:
            from pypetkitapi.water_fountain_container import SettingsFountain

            fountain.settings = SettingsFountain()

        s = fountain.status
        cfg = fountain.settings

        s.power_status = ble_status.get("power_status", s.power_status)
        s.run_status = ble_status.get("running_status", s.run_status)
        s.suspend_status = ble_status.get("suspend_status", s.suspend_status)
        s.detect_status = ble_status.get("pet_drinking", s.detect_status)

        fountain.mode = ble_status.get("mode", fountain.mode)
        fountain.is_night_no_disturbing = ble_status.get(
            "dnd_state", fountain.is_night_no_disturbing
        )
        fountain.breakdown_warning = ble_status.get(
            "warning_breakdown", fountain.breakdown_warning
        )
        fountain.lack_warning = ble_status.get(
            "warning_water_missing", fountain.lack_warning
        )
        fountain.filter_warning = ble_status.get(
            "warning_filter", fountain.filter_warning
        )
        fountain.low_battery = ble_status.get("low_battery", fountain.low_battery)

        filter_pct = ble_status.get("filter_percentage")
        if filter_pct is not None:
            fountain.filter_percent = int(filter_pct * 100)

        fountain.filter_expected_days = ble_status.get(
            "filter_time_left", fountain.filter_expected_days
        )
        fountain.water_pump_run_time = ble_status.get(
            "pump_runtime", fountain.water_pump_run_time
        )
        fountain.today_pump_run_time = ble_status.get(
            "pump_runtime_today", fountain.today_pump_run_time
        )
        fountain.expected_clean_water = ble_status.get(
            "expected_clean_water", fountain.expected_clean_water
        )
        fountain.today_clean_water = ble_status.get(
            "today_clean_water", fountain.today_clean_water
        )

        energy = ble_status.get("today_use_electricity")
        if energy is not None:
            try:
                fountain.today_use_electricity = float(energy)
            except (ValueError, TypeError):
                pass

        cfg.smart_working_time = ble_status.get("smart_time_on", cfg.smart_working_time)
        cfg.smart_sleep_time = ble_status.get("smart_time_off", cfg.smart_sleep_time)
        cfg.lamp_ring_switch = ble_status.get("led_switch", cfg.lamp_ring_switch)
        cfg.lamp_ring_brightness = ble_status.get(
            "led_brightness", cfg.lamp_ring_brightness
        )
        cfg.no_disturbing_switch = ble_status.get(
            "do_not_disturb_switch", cfg.no_disturbing_switch
        )

        # CTW3 electricity
        battery_pct = ble_status.get("battery_percentage")
        battery_v = ble_status.get("battery_voltage")
        supply_v = ble_status.get("supply_voltage")
        if any(v is not None for v in (battery_pct, battery_v, supply_v)):
            if fountain.electricity is None:
                from pypetkitapi.water_fountain_container import Electricity

                fountain.electricity = Electricity()
            if battery_pct is not None:
                fountain.electricity.battery_percent = battery_pct
            if battery_v is not None:
                fountain.electricity.battery_voltage = battery_v
            if supply_v is not None:
                fountain.electricity.supply_voltage = supply_v

    # -----------------------------------------------------------------------
    # Static helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _seconds_since_2000() -> int:
        reference = datetime(2000, 1, 1, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return int((now - reference).total_seconds())

    @staticmethod
    def _derive_secret(device_id_bytes: list[int]) -> list[int]:
        """Derive the BLE session secret from device ID bytes."""
        padded = ([0] * max(0, 8 - len(device_id_bytes)) + device_id_bytes)[:8]
        reversed_bytes = list(reversed(padded))
        if (
            len(reversed_bytes) >= 2
            and reversed_bytes[-2] == 0
            and reversed_bytes[-1] == 0
        ):
            reversed_bytes[-2] = 13
            reversed_bytes[-1] = 37
        return reversed_bytes

    @staticmethod
    def _calculate_values(
        mode: int,
        filter_pct: float,
        smart_time_on: int,
        smart_time_off: int,
        alias: str,
        pump_runtime_today: int,
        pump_runtime: int,
    ) -> tuple[int, float, float, str]:
        """Calculate filter days remaining, water purified (L), and energy (kWh)."""
        time_on = 1 if mode == 1 else smart_time_on
        time_off = 0 if mode == 1 else smart_time_off
        if time_on == 0:
            filter_days = math.ceil(filter_pct * 60)
        else:
            filter_days = math.ceil(
                ((filter_pct * 30.0) * (time_on + time_off)) / time_on
            )

        flow_rate, divisor = 1.5, 2.0
        if alias == "W5C":
            flow_rate, divisor = 1.3, 1.0
        elif alias == "W4X":
            divisor = 1.8
        elif alias == "CTW3":
            divisor = 3.0

        water_today = (flow_rate * pump_runtime_today / 60.0) / divisor
        water_total = (flow_rate * pump_runtime / 60.0) / divisor

        power_coeff = 0.182 if alias == "W5C" else 0.75
        energy = format(power_coeff * pump_runtime / 3_600_000.0, "f")

        return filter_days, water_total, water_today, energy
