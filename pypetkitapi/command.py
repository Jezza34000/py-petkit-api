"""Command module for PyPetkit"""

from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
from enum import IntEnum, StrEnum
import json
import struct
import time

from pypetkitapi.const import (
    ALL_DEVICES,
    D3,
    D4H,
    D4S,
    D4SH,
    DEVICES_FEEDER,
    FEEDER,
    FEEDER_MINI,
    K2,
    K3,
    PET,
    T3,
    T4,
    T5,
    T6,
    T7,
    TEMP_CAMERA_TYPES,
    PetkitEndpoint,
)


class DeviceCommand(StrEnum):
    """Device Command"""

    POWER = "power_device"
    CONTROL_DEVICE = "control_device"
    UPDATE_SETTING = "update_setting"
    OPEN_CAMERA = "open_camera"


class FountainCommand(StrEnum):
    """Device Command"""

    CONTROL_DEVICE = "control_device"


class FeederCommand(StrEnum):
    """Specific Feeder Command"""

    CALL_PET = "call_pet"
    CALIBRATION = "food_reset"
    MANUAL_FEED = "manual_feed"
    MANUAL_FEED_DUAL = "manual_feed_dual"
    CANCEL_MANUAL_FEED = "cancelRealtimeFeed"
    FOOD_REPLENISHED = "food_replenished"
    RESET_DESICCANT = "desiccant_reset"
    REMOVE_DAILY_FEED = "remove_daily_feed"
    RESTORE_DAILY_FEED = "restore_daily_feed"
    PLAY_SOUND = "play_sound"


class LitterCommand(StrEnum):
    """Specific LitterCommand"""

    RESET_N50_DEODORIZER = "reset_deodorizer"
    # T5/T6 N60 does not have this command, must use control_device


class PetCommand(StrEnum):
    """Specific PetCommand"""

    PET_UPDATE_SETTING = "pet_update_setting"


class LBCommand(IntEnum):
    """LitterBoxCommand"""

    CLEANING = 0
    DUMPING = 1
    ODOR_REMOVAL = 2  # For T4=K3 spray, for T5/T6=N60 fan
    RESETTING = 3
    LEVELING = 4
    CALIBRATING = 5
    RESET_DEODOR = 6
    LIGHT = 7
    RESET_N50_DEODOR = 8
    MAINTENANCE = 9
    RESET_N60_DEODOR = 10


class PurMode(IntEnum):
    """Purifier working mode"""

    AUTO_MODE = 0
    SILENT_MODE = 1
    STANDARD_MODE = 2
    STRONG_MODE = 3


class DeviceAction(StrEnum):
    """Device action for LitterBox and Purifier"""

    # LitterBox only
    CONTINUE = "continue_action"
    END = "end_action"
    START = "start_action"
    STOP = "stop_action"
    # Purifier K2 only
    MODE = "mode_action"
    # All devices
    POWER = "power_action"


class FountainAction(StrEnum):
    """Fountain Action — covers every BLE command of the W5/CTW2 protocol.

    Legend
    ------
    CMD xxx  = BLE command ID as defined in W5_BLE_PROTOCOL.md
    (read)   = no payload, device replies with data
    (write)  = device-modifying command
    (param)  = parametric command, use FOUNTAIN_COMMAND_PARAMS +
                BleFountainHelper to build the payload
    """

    # ------------------------------------------------------------------ #
    # Legacy / already-present actions (kept for backward compatibility)  #
    # ------------------------------------------------------------------ #
    MODE_NORMAL = "Normal"
    MODE_SMART = "Smart"
    MODE_STANDARD = "Standard"
    MODE_INTERMITTENT = "Intermittent"
    PAUSE = "Pause"
    CONTINUE = "Continue"
    POWER_OFF = "Power Off"
    POWER_ON = "Power On"
    RESET_FILTER = "Reset Filter"       # CMD 222 (write)
    DO_NOT_DISTURB = "Do Not Disturb"
    DO_NOT_DISTURB_OFF = "Do Not Disturb Off"
    LIGHT_LOW = "Light Low"
    LIGHT_MEDIUM = "Light Medium"
    LIGHT_HIGH = "Light High"
    LIGHT_ON = "Light On"
    LIGHT_OFF = "Light Off"

    # ------------------------------------------------------------------ #
    # Read commands (request → response, no payload sent)                #
    # ------------------------------------------------------------------ #
    GET_DEVICE_ID = "Get Device ID"          # CMD 213 — device ID + serial
    GET_VERSION = "Get Version"              # CMD 200 — hw/fw version
    GET_STATE = "Get State"                  # CMD 210 — running state
    GET_SETTINGS = "Get Settings"           # CMD 211 — all settings
    GET_VOLTAGE = "Get Voltage"             # CMD 66  — raw ADC voltage
    GET_EXT_LIGHT = "Get Ext Light"         # CMD 215 — extended light schedule
    GET_EXT_DND = "Get Ext DND"             # CMD 216 — extended DND schedule

    # ------------------------------------------------------------------ #
    # Auth / setup commands                                              #
    # ------------------------------------------------------------------ #
    AUTH_ZERO_SECRET = "Auth Zero Secret"    # CMD 86  — authenticate with 8×0x00
    TIME_SYNC = "Time Sync"                  # CMD 84  — sync RTC (param)

    # ------------------------------------------------------------------ #
    # Mode / power commands  (CMD 220)                                   #
    # ------------------------------------------------------------------ #
    SET_MODE_OFF = "Set Mode Off"            # CMD 220 mode=0
    SET_MODE_NORMAL = "Set Mode Normal"      # CMD 220 mode=1
    SET_MODE_SMART = "Set Mode Smart"        # CMD 220 mode=2

    # ------------------------------------------------------------------ #
    # Write-all-settings  (CMD 221 — param)                              #
    # Use BleFountainHelper.build_cmd221_payload()                       #
    # ------------------------------------------------------------------ #
    WRITE_SETTINGS = "Write Settings"        # CMD 221 (param)

    # ------------------------------------------------------------------ #
    # Extended schedule writes  (CMD 225 / 226 — param)                  #
    # Use BleFountainHelper.build_cmd225_payload / build_cmd226_payload  #
    # ------------------------------------------------------------------ #
    WRITE_EXT_LIGHT = "Write Ext Light"      # CMD 225 (param)
    WRITE_EXT_DND = "Write Ext DND"          # CMD 226 (param)

    # ------------------------------------------------------------------ #
    # Device initialisation  (CMD 73 — DANGEROUS, writes permanently)   #
    # ------------------------------------------------------------------ #
    DEVICE_INIT = "Device Init"              # CMD 73  (param)


# ---------------------------------------------------------------------------
# FOUNTAIN_COMMAND  — fixed-payload commands
#
# Format inside the list:
#   [cmd_id, type_byte, payload_byte_0, payload_byte_1, ...]
#
# The framing (BLE_START_TRAME / counter / length / BLE_END_TRAME) is added
# by BluetoothManager.get_ble_cmd_data() exactly as before.
#
# Packet wire format (reminder):
#   FA FC FD  <cmd:1>  <type:1>  <seq:1>  <len_lo:1>  <len_hi:1>  [data]  FB
#   type=1 → Request,  type=2 → Response,  type=3 → Non-response request
# ---------------------------------------------------------------------------
FOUNTAIN_COMMAND: dict[FountainAction, list[int]] = {
    # ------------------------------------------------------------------
    # Backward-compatible entries (unchanged)
    # ------------------------------------------------------------------
    FountainAction.PAUSE:        [220, 1, 3, 0, 1, 0, 2],
    FountainAction.CONTINUE:     [220, 1, 3, 0, 1, 1, 2],
    FountainAction.RESET_FILTER: [222, 1, 0, 0],
    FountainAction.POWER_OFF:    [220, 1, 3, 0, 0, 1, 1],
    FountainAction.POWER_ON:     [220, 1, 3, 0, 1, 1, 1],

    # ------------------------------------------------------------------
    # Read commands  (CMD type=1, payload empty → len=0x00 0x00)
    # Format: [cmd_id, type=1, len_lo=0, len_hi=0]
    # The counter byte is injected by get_ble_cmd_data() at index 2.
    # ------------------------------------------------------------------
    FountainAction.GET_DEVICE_ID:    [213, 1, 0, 0],
    FountainAction.GET_VERSION:      [200, 1, 0, 0],
    FountainAction.GET_STATE:        [210, 1, 0, 0],
    FountainAction.GET_SETTINGS:     [211, 1, 0, 0],
    FountainAction.GET_VOLTAGE:      [66,  1, 0, 0],
    FountainAction.GET_EXT_LIGHT:    [215, 1, 0, 0],
    FountainAction.GET_EXT_DND:      [216, 1, 0, 0],

    # ------------------------------------------------------------------
    # Auth — CMD 86 with 8 zero bytes  (works on un-initialised devices)
    # payload = 8×0x00
    # ------------------------------------------------------------------
    FountainAction.AUTH_ZERO_SECRET: [86, 1, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    # ------------------------------------------------------------------
    # Mode changes  (CMD 220)
    # payload structure: [mode, submode]
    #   mode 0 = off, 1 = normal, 2 = smart
    # ------------------------------------------------------------------
    FountainAction.SET_MODE_OFF:    [220, 1, 2, 0, 0, 0],
    FountainAction.SET_MODE_NORMAL: [220, 1, 2, 0, 1, 0],
    FountainAction.SET_MODE_SMART:  [220, 1, 2, 0, 2, 0],
}

# ---------------------------------------------------------------------------
# FOUNTAIN_COMMAND_PARAMS  — commands that require a dynamically-built payload
#
# These are NOT in FOUNTAIN_COMMAND because their payload depends on runtime
# arguments supplied by the caller.  Use the BleFountainHelper helpers below
# to build the payload list, then call
# BluetoothManager.send_ble_command_raw(fountain_id, payload_list).
# ---------------------------------------------------------------------------
FOUNTAIN_COMMAND_PARAMS: dict[FountainAction, int] = {
    FountainAction.WRITE_SETTINGS:  221,   # CMD 221 — write all settings blob
    FountainAction.WRITE_EXT_LIGHT: 225,   # CMD 225 — write extended light schedule
    FountainAction.WRITE_EXT_DND:   226,   # CMD 226 — write extended DND schedule
    FountainAction.TIME_SYNC:        84,   # CMD 84  — time sync
    FountainAction.DEVICE_INIT:      73,   # CMD 73  — one-time device initialisation
}


class BleFountainHelper:
    """Static helpers to build parametric BLE payload *lists* for W5/CTW2 fountains.

    Every helper returns a ``list[int]`` that starts with the command header
    bytes expected by :meth:`BluetoothManager.get_ble_cmd_data`, i.e.:

        [cmd_id, type_byte, len_lo, len_hi, <payload bytes…>]

    The BLE framing (``FA FC FD`` header, sequence counter, ``FB`` trailer)
    is **not** included — it is added by the caller as usual.

    Time fields
    -----------
    All "time" parameters are expressed in **minutes from midnight** (0–1439)
    to match the wire protocol (big-endian uint16 in the GATT frame).

    Protocol reference
    ------------------
    mr-ransel/petkit-ble-reverse-engineering — W5_BLE_PROTOCOL.md
    """

    # ------------------------------------------------------------------ #
    # CMD 221 — Write all settings (13 or 14 bytes)                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_cmd221_payload(
        *,
        smart_working_time: int,
        smart_sleep_time: int,
        lamp_ring_switch: int,
        lamp_ring_brightness: int,
        lamp_ring_light_up_time: int,
        lamp_ring_go_out_time: int,
        no_disturbing_switch: int,
        no_disturbing_start_time: int,
        no_disturbing_end_time: int,
        is_lock: int | None = None,
    ) -> list[int]:
        """Build a CMD 221 payload list ready for get_ble_cmd_data().

        Parameters
        ----------
        smart_working_time:
            Smart-mode pump-on duration in minutes (0-255).
        smart_sleep_time:
            Smart-mode pump-off (sleep) duration in minutes (0-255).
        lamp_ring_switch:
            LED ring on/off: 0=off, 1=on.
        lamp_ring_brightness:
            LED brightness 0-255.
        lamp_ring_light_up_time:
            LED-on time in minutes from midnight (0-1439).
        lamp_ring_go_out_time:
            LED-off time in minutes from midnight (0-1439).
        no_disturbing_switch:
            Do-not-disturb on/off: 0=off, 1=on.
        no_disturbing_start_time:
            DND start time in minutes from midnight (0-1439).
        no_disturbing_end_time:
            DND end time in minutes from midnight (0-1439).
        is_lock:
            Child lock: 0=off, 1=on. Pass ``None`` to omit (13-byte form).

        Returns
        -------
        list[int]
            Payload list: [221, 1, len_lo, len_hi, b0..b12 (or b13)].
        """
        data = bytearray()
        data.append(smart_working_time & 0xFF)
        data.append(smart_sleep_time & 0xFF)
        data.append(lamp_ring_switch & 0xFF)
        data.append(lamp_ring_brightness & 0xFF)
        data.extend(struct.pack(">H", lamp_ring_light_up_time))
        data.extend(struct.pack(">H", lamp_ring_go_out_time))
        data.append(no_disturbing_switch & 0xFF)
        data.extend(struct.pack(">H", no_disturbing_start_time))
        data.extend(struct.pack(">H", no_disturbing_end_time))
        if is_lock is not None:
            data.append(is_lock & 0xFF)
        payload_len = len(data)
        return [221, 1, payload_len & 0xFF, (payload_len >> 8) & 0xFF, *data]

    # ------------------------------------------------------------------ #
    # CMD 225 — Write extended light schedule                            #
    # CMD 226 — Write extended DND schedule                              #
    # (same structure, different command ID)                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_ext_schedule_payload(
        cmd_id: int,
        config_mode: int,
        time_slots: list[tuple[int, int]],
    ) -> list[int]:
        """Internal helper shared by CMD 225 and CMD 226.

        Parameters
        ----------
        cmd_id:
            225 for light schedule, 226 for DND schedule.
        config_mode:
            1 = config mode 1, 0 = config mode 2 (matches lightConfig /
            disturbConfig in the GET response).
        time_slots:
            List of (start_minutes, end_minutes) tuples.  Max 10 slots.
            Times are minutes from midnight (0-1439).
        """
        data = bytearray()
        data.append(config_mode & 0xFF)
        data.append(len(time_slots) & 0xFF)
        data.extend(b"\x00" * 4)  # 4 reserved bytes
        for start, end in time_slots:
            data.extend(struct.pack(">H", start))
            data.extend(struct.pack(">H", end))
            data.append(0x00)  # reserved per-slot byte
        payload_len = len(data)
        return [cmd_id, 1, payload_len & 0xFF, (payload_len >> 8) & 0xFF, *data]

    @staticmethod
    def build_cmd225_payload(
        config_mode: int,
        time_slots: list[tuple[int, int]],
    ) -> list[int]:
        """Build a CMD 225 payload (extended light schedule).

        Parameters
        ----------
        config_mode:
            1 or 0 — matches the ``lightConfig`` field returned by CMD 215.
        time_slots:
            Up to 10 ``(start_minutes, end_minutes)`` tuples.
        """
        return BleFountainHelper._build_ext_schedule_payload(225, config_mode, time_slots)

    @staticmethod
    def build_cmd226_payload(
        config_mode: int,
        time_slots: list[tuple[int, int]],
    ) -> list[int]:
        """Build a CMD 226 payload (extended DND schedule).

        Parameters
        ----------
        config_mode:
            1 or 0 — matches the ``disturbConfig`` field returned by CMD 216.
        time_slots:
            Up to 10 ``(start_minutes, end_minutes)`` tuples.
        """
        return BleFountainHelper._build_ext_schedule_payload(226, config_mode, time_slots)

    # ------------------------------------------------------------------ #
    # CMD 84 — Time sync                                                 #
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_cmd84_payload(utc_offset_hours: int | None = None) -> list[int]:
        """Build a CMD 84 time-sync payload.

        The device clock is referenced to 2000-01-01T00:00:00 UTC.  The
        timezone byte encodes ``UTC_offset_hours + 12`` (so UTC+0 = 12,
        UTC+2 = 14, UTC-5 = 7 …).

        Parameters
        ----------
        utc_offset_hours:
            Integer UTC offset of the local timezone (e.g. +1 for CET,
            +2 for CEST, -5 for EST).  When *None* the system timezone is
            used via ``time.timezone``.
        """
        from datetime import timezone as _tz, datetime as _dt

        epoch_2000 = _dt(2000, 1, 1, tzinfo=_tz.utc).timestamp()
        now = _dt.now(_tz.utc).timestamp()
        seconds_since_2000 = int(now - epoch_2000)

        if utc_offset_hours is None:
            utc_offset_hours = int(-time.timezone / 3600)

        tz_byte = (int(utc_offset_hours) + 12) & 0xFF

        data = bytearray()
        data.append(0x00)                                   # reserved
        data.extend(struct.pack(">i", seconds_since_2000))  # 4 bytes, big-endian signed
        data.append(tz_byte)
        payload_len = len(data)  # always 6
        return [84, 1, payload_len & 0xFF, (payload_len >> 8) & 0xFF, *data]

    # ------------------------------------------------------------------ #
    # CMD 73 — Device initialisation  (WRITES PERMANENTLY — use wisely) #
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_cmd73_payload(device_id: int, secret: bytes) -> list[int]:
        """Build a CMD 73 one-time initialisation payload.

        .. warning::
            This command **permanently** writes the device ID and secret into
            the fountain's non-volatile memory.  It can only be undone by a
            **physical factory reset** of the device.  After calling this,
            the zero-secret shortcut (CMD 86 with 8 null bytes) will no
            longer work, and you **must** store the chosen secret safely.

        Parameters
        ----------
        device_id:
            64-bit integer device ID to write (big-endian on the wire).
        secret:
            Exactly 8 bytes of secret.  Shorter values are zero-padded;
            longer values are truncated.
        """
        id_bytes = struct.pack(">q", device_id)
        secret_padded = (secret + b"\x00" * 8)[:8]
        data = id_bytes + secret_padded
        payload_len = len(data)  # always 16
        return [73, 1, payload_len & 0xFF, (payload_len >> 8) & 0xFF, *data]


@dataclass
class CmdData:
    """Command Info"""

    endpoint: str | Callable
    params: Callable
    supported_device: list[str] = field(default_factory=list)


def get_endpoint_manual_feed(device):
    """Get the endpoint for the device"""
    if device.device_nfo.device_type in [FEEDER_MINI, FEEDER]:
        return PetkitEndpoint.MANUAL_FEED_OLD  # Old endpoint snakecase
    return PetkitEndpoint.MANUAL_FEED_NEW  # New endpoint camelcase


def get_endpoint_reset_desiccant(device):
    """Get the endpoint for the device"""
    if device.device_nfo.device_type in [FEEDER_MINI, FEEDER]:
        return PetkitEndpoint.DESICCANT_RESET_OLD  # Old endpoint snakecase
    return PetkitEndpoint.DESICCANT_RESET_NEW  # New endpoint camelcase


def get_endpoint_update_setting(device):
    """Get the endpoint for the device"""
    if device.device_nfo.device_type in [FEEDER_MINI, K3]:
        return PetkitEndpoint.UPDATE_SETTING_OLD
    return PetkitEndpoint.UPDATE_SETTING


ACTIONS_MAP = {
    DeviceCommand.UPDATE_SETTING: CmdData(
        endpoint=get_endpoint_update_setting,
        params=lambda device, setting: {
            "id": device.id,
            "kv": json.dumps(setting),
        },
        supported_device=ALL_DEVICES,
    ),
    DeviceCommand.CONTROL_DEVICE: CmdData(
        endpoint=PetkitEndpoint.CONTROL_DEVICE,
        params=lambda device, command: {
            "id": device.id,
            "kv": json.dumps(command),
            "type": list(command.keys())[0].split("_")[0],
        },
        supported_device=[K2, K3, T3, T4, T5, T6, T7],
    ),
    DeviceCommand.OPEN_CAMERA: CmdData(
        endpoint=PetkitEndpoint.TEMP_OPEN_CAMERA,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=TEMP_CAMERA_TYPES,
    ),
    FeederCommand.REMOVE_DAILY_FEED: CmdData(
        endpoint=PetkitEndpoint.REMOVE_DAILY_FEED,
        params=lambda device, setting: {
            "deviceId": device.id,
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            **setting,  # Need the id of the feed to remove
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.RESTORE_DAILY_FEED: CmdData(
        endpoint=PetkitEndpoint.RESTORE_DAILY_FEED,
        params=lambda device, setting: {
            "deviceId": device.id,
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            **setting,  # Need the id of the feed to restore
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.MANUAL_FEED: CmdData(
        endpoint=get_endpoint_manual_feed,
        params=lambda device, setting: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            "name": "",
            "time": "-1",
            **setting,
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.CANCEL_MANUAL_FEED: CmdData(
        endpoint=lambda device: (
            PetkitEndpoint.FRESH_ELEMENT_CANCEL_FEED
            if device.device_nfo.device_type == FEEDER
            else PetkitEndpoint.CANCEL_FEED
        ),
        params=lambda device: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            **(
                {"id": device.manual_feed_id}
                if device.device_nfo.device_type in [D4H, D4S, D4SH]
                else {}
            ),
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.FOOD_REPLENISHED: CmdData(
        endpoint=PetkitEndpoint.REPLENISHED_FOOD,
        params=lambda device: {
            "deviceId": device.id,
            "noRemind": "3",
        },
        supported_device=[D4H, D4S, D4SH],
    ),
    FeederCommand.CALIBRATION: CmdData(
        endpoint=PetkitEndpoint.FRESH_ELEMENT_CALIBRATION,
        params=lambda device, value: {
            "deviceId": device.id,
            "action": value,
        },
        supported_device=[FEEDER],
    ),
    FeederCommand.RESET_DESICCANT: CmdData(
        endpoint=get_endpoint_reset_desiccant,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.PLAY_SOUND: CmdData(
        endpoint=PetkitEndpoint.PLAY_SOUND,
        params=lambda device, sound_id: {
            "soundId": sound_id,
            "deviceId": device.id,
        },
        supported_device=[D3, D4H, D4SH],
    ),
    FeederCommand.CALL_PET: CmdData(
        endpoint=PetkitEndpoint.CALL_PET,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=[D3],
    ),
    LitterCommand.RESET_N50_DEODORIZER: CmdData(
        endpoint=PetkitEndpoint.DEODORANT_RESET,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=[T4, T5, T6],
    ),
    PetCommand.PET_UPDATE_SETTING: CmdData(
        endpoint=PetkitEndpoint.PET_UPDATE_SETTING,
        params=lambda pet, setting: {
            "petId": pet.pet_id,
            "kv": json.dumps(setting),
        },
        supported_device=[PET],
    ),
}
