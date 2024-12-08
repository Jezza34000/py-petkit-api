"""Command module for PyPetkit"""

from dataclasses import dataclass, field
import datetime
from enum import StrEnum
import json
from typing import Callable

from pypetkit.const import (
    ALL_DEVICES,
    D4H,
    D4S,
    D4SH,
    DEVICES_FEEDER,
    FEEDER,
    T4,
    T5,
    T6,
    PetkitEndpoint,
)


class DeviceCommand(StrEnum):
    """Device Command"""

    UPDATE_SETTING = "update_setting"


class FeederCommand(StrEnum):
    """Feeder Command"""

    CALIBRATION = "food_reset"
    CANCEL_MANUAL_FEED = "cancelRealtimeFeed"
    FOOD_REPLENISHED = "food_replenished"
    RESET_DESICCANT = "desiccantReset"


class LitterCommand(StrEnum):
    """LitterCommand"""

    RESET_DEODORIZER = "reset_deodorizer"


@dataclass
class CmdData:
    """Command Info"""

    endpoint: str  # TODO: Support many endpoints
    params: Callable
    supported_device: list[str] = field(default_factory=list)


ACTIONS_MAP = {
    DeviceCommand.UPDATE_SETTING: CmdData(
        endpoint=PetkitEndpoint.UPDATE_SETTING,
        params=lambda device, setting: {
            "id": device.id,
            "kv": json.dumps(setting),
        },
        supported_device=ALL_DEVICES,
    ),
    FeederCommand.CANCEL_MANUAL_FEED: CmdData(
        endpoint=PetkitEndpoint.CANCEL_FEED,  # TODO: Support many endpoints
        params=lambda device: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            "id": None,  # TODO : Find the last manual feed id
        },
        supported_device=[D4H, D4S, D4SH],
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
        endpoint=PetkitEndpoint.FRESH_ELEMENT_CALIBRATION,
        params=lambda device, value: {
            "deviceId": device.id,
            "action": value,
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
    # LitterCommand.CONTROL_DEVICE: CmdData(
    #     endpoint=PetkitEndpoint.CONTROL_DEVICE,
    #     params=lambda device, setting: {
    #         "id": device.id,
    #         "kv": json.dumps(setting),
    #         "type": LB_CMD_TO_TYPE[command],
    #     },
    #     supported_device=[T3, T4, T5, T6],
    # ),
    # FountainCommand.CONTROL_DEVICE: CmdData(
    #     endpoint=PetkitEndpoint.CONTROL_DEVICE,
    #     params=lambda device, setting: {
    #         "bleId": water_fountain.data["id"],
    #         "cmd": cmnd_code,
    #         "data": ble_data,
    #         "mac": water_fountain.data["mac"],
    #         "type": water_fountain.ble_relay,
    #     },
    #     supported_device=[CTW3],
    # ),
}
