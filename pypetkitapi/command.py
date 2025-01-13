"""Command module for PyPetkit"""

from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
from enum import IntEnum, StrEnum
import json

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
    T3,
    T4,
    T5,
    T6,
    PetkitEndpoint,
)


class DeviceCommand(StrEnum):
    """Device Command"""

    POWER = "power_device"
    CONTROL_DEVICE = "control_device"
    UPDATE_SETTING = "update_setting"


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


class LitterCommand(StrEnum):
    """Specific LitterCommand"""

    RESET_DEODORIZER = "reset_deodorizer"


class PetCommand(StrEnum):
    """Specific PetCommand"""

    PET_UPDATE_SETTING = "pet_update_setting"


class LBCommand(IntEnum):
    """LitterBoxCommand"""

    CLEANING = 0
    DUMPING = 1
    ODOR_REMOVAL = 2
    RESETTING = 3
    LEVELING = 4
    CALIBRATING = 5
    RESET_DEODOR = 6
    LIGHT = 7
    RESET_MAX_DEODOR = 8
    MAINTENANCE = 9


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
    # Purifier only
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
    if device.device_nfo.device_type == FEEDER_MINI:
        return PetkitEndpoint.UPDATE_SETTING_FEEDER_MINI
    return PetkitEndpoint.UPDATE_SETTING


ACTIONS_MAP = {
    DeviceCommand.UPDATE_SETTING: CmdData(
        endpoint=lambda device: get_endpoint_update_setting(device),
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
        supported_device=[K2, K3, T3, T4, T5, T6],
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
        endpoint=lambda device: get_endpoint_manual_feed(device),
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
        endpoint=lambda device: get_endpoint_reset_desiccant(device),
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=DEVICES_FEEDER,
    ),
    LitterCommand.RESET_DEODORIZER: CmdData(
        endpoint=PetkitEndpoint.DEODORANT_RESET,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=[T4, T5, T6],
    ),
    FeederCommand.CALL_PET: CmdData(
        endpoint=PetkitEndpoint.CALL_PET,
        params=lambda device: {
            "deviceId": device.id,
        },
        supported_device=[D3],
    ),
    PetCommand.PET_UPDATE_SETTING: CmdData(
        endpoint=PetkitEndpoint.CONTROL_DEVICE,
        params=lambda pet, setting: {
            "petId": pet,
            "kv": json.dumps(setting),
        },
        supported_device=ALL_DEVICES,
    ),
}
