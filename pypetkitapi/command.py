"""Command module for PyPetkit"""

from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
from enum import IntEnum, StrEnum
import json

from pypetkitapi.const import (
    ALL_DEVICES,
    COZY,
    D3,
    D4H,
    D4S,
    D4SH,
    DEVICES_FEEDER,
    DUAL_HOPPER_DEVICES,
    FEEDER,
    FEEDER_MINI,
    K2,
    K3,
    MANUAL_FEED_DEFAULT_VALID_VALUES,
    MANUAL_FEED_VALID_VALUES,
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
    SAVE_FEED = "save_feed"
    SUSPEND_FEED = "suspend_feed"
    RESTORE_FEED = "restore_feed"
    SAVE_REPEATS = "save_repeats"
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
    """Fountain Action"""

    MODE_NORMAL = "Normal"
    MODE_SMART = "Smart"
    MODE_STANDARD = "Standard"
    MODE_INTERMITTENT = "Intermittent"
    PAUSE = "Pause"
    CONTINUE = "Continue"
    POWER_OFF = "Power Off"
    POWER_ON = "Power On"
    RESET_FILTER = "Reset Filter"
    DO_NOT_DISTURB = "Do Not Disturb"
    DO_NOT_DISTURB_OFF = "Do Not Disturb Off"
    LIGHT_LOW = "Light Low"
    LIGHT_MEDIUM = "Light Medium"
    LIGHT_HIGH = "Light High"
    LIGHT_ON = "Light On"
    LIGHT_OFF = "Light Off"


FOUNTAIN_COMMAND = {
    FountainAction.PAUSE: [220, 1, 3, 0, 1, 0, 2],
    FountainAction.CONTINUE: [220, 1, 3, 0, 1, 1, 2],
    FountainAction.RESET_FILTER: [222, 1, 0, 0],
    FountainAction.POWER_OFF: [220, 1, 3, 0, 0, 1, 1],
    FountainAction.POWER_ON: [220, 1, 3, 0, 1, 1, 1],
    FountainAction.MODE_NORMAL: [220, 1, 3, 0, 1, 1, 1],
    FountainAction.MODE_SMART: [220, 1, 3, 0, 1, 2, 1],
    FountainAction.MODE_STANDARD: [220, 1, 3, 0, 1, 1, 1],
    FountainAction.MODE_INTERMITTENT: [220, 1, 3, 0, 1, 2, 1],
}


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


def get_endpoint_suspend_feed(device):
    """Get the suspend feed endpoint for the device."""
    if device.device_nfo.device_type in [FEEDER_MINI, FEEDER]:
        return PetkitEndpoint.SUSPEND_FEED_OLD
    return PetkitEndpoint.SUSPEND_FEED_NEW


def get_endpoint_restore_feed(device):
    """Get the restore feed endpoint for the device."""
    if device.device_nfo.device_type in [FEEDER_MINI, FEEDER]:
        return PetkitEndpoint.RESTORE_FEED_OLD
    return PetkitEndpoint.RESTORE_FEED_NEW


def get_endpoint_save_repeats(device):
    """Get the save repeats endpoint for the device."""
    if device.device_nfo.device_type in [FEEDER_MINI, FEEDER]:
        return PetkitEndpoint.SAVE_REPEATS_OLD
    return PetkitEndpoint.SAVE_REPEATS_NEW


def validate_manual_feed_amount(
    device,
    setting: dict[str, int],
) -> None:
    """Validate the manual feed amount and parameter keys for the given device type.

    Raises:
        ValueError: If the amount is not valid for the device type.
        ValueError: If the wrong amount key is used for the device type
                    (amount vs amount1/amount2).
    """
    device_type = device.device_nfo.device_type

    # --- Vérification des clés (hopper simple vs dual) ---
    is_dual = device_type in DUAL_HOPPER_DEVICES
    has_single_key = "amount" in setting
    has_dual_keys = "amount1" in setting or "amount2" in setting

    if is_dual and has_single_key:
        raise ValueError(
            f"Device type '{device_type}' is a dual hopper feeder: "
            f"use 'amount1' and/or 'amount2', not 'amount'."
        )
    if not is_dual and has_dual_keys:
        raise ValueError(
            f"Device type '{device_type}' is a single hopper feeder: "
            f"use 'amount', not 'amount1'/'amount2'."
        )

    # --- Vérification de la valeur ---
    amount: int = (
        setting.get("amount") or setting.get("amount1") or setting.get("amount2") or 0
    )
    valid_values = MANUAL_FEED_VALID_VALUES.get(
        device_type, MANUAL_FEED_DEFAULT_VALID_VALUES
    )
    if amount not in valid_values:
        raise ValueError(
            f"Feeding amount '{amount}' is not valid for device type '{device_type}'. "
            f"Valid values are: {valid_values}"
        )


def build_manual_feed_params(
    device,
    setting: dict[str, int],
) -> dict[str, str]:
    """Build and validate the manual feed params for the given device type."""
    validate_manual_feed_amount(device, setting)
    return {
        "day": datetime.datetime.now().strftime("%Y%m%d"),
        "deviceId": device.id,
        "name": "",
        "time": "-1",
        **setting,
    }


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
        supported_device=[K2, K3, T3, T4, T5, T6, T7, COZY],
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
        params=build_manual_feed_params,
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
    FeederCommand.SAVE_FEED: CmdData(
        endpoint=PetkitEndpoint.SAVE_FEED,
        params=lambda device, feed_daily_list: {
            "deviceId": device.id,
            "feedDailyList": json.dumps(feed_daily_list),
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.SUSPEND_FEED: CmdData(
        endpoint=get_endpoint_suspend_feed,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.RESTORE_FEED: CmdData(
        endpoint=get_endpoint_restore_feed,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=DEVICES_FEEDER,
    ),
    FeederCommand.SAVE_REPEATS: CmdData(
        endpoint=get_endpoint_save_repeats,
        params=lambda device, setting: {
            "deviceId": device.id,
            **setting,
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
