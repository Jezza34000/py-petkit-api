"""Command module for PyPetkit"""

from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
from enum import StrEnum
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
    T3,
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

    CALL_PET = "call_pet"
    CALIBRATION = "food_reset"
    MANUAL_FEED = "manual_feed"
    MANUAL_FEED_DUAL = "manual_feed_dual"
    CANCEL_MANUAL_FEED = "cancelRealtimeFeed"
    FOOD_REPLENISHED = "food_replenished"
    RESET_DESICCANT = "desiccantReset"


class LitterCommand(StrEnum):
    """LitterCommand"""

    CONTROL_DEVICE = "control_device"
    RESET_DEODORIZER = "reset_deodorizer"


class PetCommand(StrEnum):
    """PetCommand"""

    UPDATE_SETTING = "update_setting"


class LitterBoxCommand(StrEnum):
    """LitterBoxCommand"""

    LIGHT_ON = "light_on"
    ODOR_REMOVAL = "start_odor"
    PAUSE_CLEAN = "stop_clean"
    POWER = "power"
    RESET_DEODOR = "reset_deodorizer"
    RESUME_CLEAN = "continue_clean"
    START_CLEAN = "start_clean"
    START_MAINTENANCE = "start_maintenance"
    EXIT_MAINTENANCE = "exit_maintenance"
    PAUSE_MAINTENANCE_EXIT = "pause_maintenance_exit"
    RESUME_MAINTENANCE_EXIT = "resume_maintenance_exit"
    DUMP_LITTER = "dump_litter"
    PAUSE_LITTER_DUMP = "pause_litter_dump"
    RESUME_LITTER_DUMP = "resume_litter_dump"
    RESET_MAX_DEODOR = "reset_max_deodorizer"


class LitterBoxCommandKey(StrEnum):
    """LitterBoxCommandKey"""

    CONTINUE = "continue_action"
    END = "end_action"
    POWER = "power_action"
    START = "start_action"
    STOP = "stop_action"


class LitterBoxCommandType(StrEnum):
    """LitterBoxCommandType"""

    CONTINUE = "continue"
    END = "end"
    POWER = "power"
    START = "start"
    STOP = "stop"


LB_CMD_TO_KEY = {
    LitterBoxCommand.LIGHT_ON: LitterBoxCommandKey.START,
    LitterBoxCommand.POWER: LitterBoxCommandKey.POWER,
    LitterBoxCommand.START_CLEAN: LitterBoxCommandKey.START,
    LitterBoxCommand.PAUSE_CLEAN: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_CLEAN: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.ODOR_REMOVAL: LitterBoxCommandKey.START,
    LitterBoxCommand.RESET_DEODOR: LitterBoxCommandKey.START,
    LitterBoxCommand.START_MAINTENANCE: LitterBoxCommandKey.START,
    LitterBoxCommand.EXIT_MAINTENANCE: LitterBoxCommandKey.END,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.DUMP_LITTER: LitterBoxCommandKey.START,
    LitterBoxCommand.PAUSE_LITTER_DUMP: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_LITTER_DUMP: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.RESET_MAX_DEODOR: LitterBoxCommandKey.START,
}

LB_CMD_TO_TYPE = {
    LitterBoxCommand.LIGHT_ON: LitterBoxCommandType.START,
    LitterBoxCommand.POWER: LitterBoxCommandType.POWER,
    LitterBoxCommand.START_CLEAN: LitterBoxCommandType.START,
    LitterBoxCommand.PAUSE_CLEAN: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_CLEAN: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.ODOR_REMOVAL: LitterBoxCommandType.START,
    LitterBoxCommand.RESET_DEODOR: LitterBoxCommandType.START,
    LitterBoxCommand.START_MAINTENANCE: LitterBoxCommandType.START,
    LitterBoxCommand.EXIT_MAINTENANCE: LitterBoxCommandType.END,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.DUMP_LITTER: LitterBoxCommandType.START,
    LitterBoxCommand.PAUSE_LITTER_DUMP: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_LITTER_DUMP: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.RESET_MAX_DEODOR: LitterBoxCommandType.START,
}

LB_CMD_TO_VALUE = {
    LitterBoxCommand.LIGHT_ON: 7,
    LitterBoxCommand.START_CLEAN: 0,
    LitterBoxCommand.PAUSE_CLEAN: 0,
    LitterBoxCommand.RESUME_CLEAN: 0,
    LitterBoxCommand.ODOR_REMOVAL: 2,
    LitterBoxCommand.RESET_DEODOR: 6,
    LitterBoxCommand.START_MAINTENANCE: 9,
    LitterBoxCommand.EXIT_MAINTENANCE: 9,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: 9,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: 9,
    LitterBoxCommand.DUMP_LITTER: 1,
    LitterBoxCommand.PAUSE_LITTER_DUMP: 1,
    LitterBoxCommand.RESUME_LITTER_DUMP: 1,
    LitterBoxCommand.RESET_MAX_DEODOR: 8,
}


@dataclass
class CmdData:
    """Command Info"""

    endpoint: str | Callable
    params: Callable
    supported_device: list[str] = field(default_factory=list)


def get_endpoint_manual_feed(device):
    """Get the endpoint for the device"""
    if device.device_type == FEEDER_MINI:
        return PetkitEndpoint.MINI_MANUAL_FEED
    if device.device_type == FEEDER:
        return PetkitEndpoint.FRESH_ELEMENT_MANUAL_FEED
    return PetkitEndpoint.MANUAL_FEED


def get_endpoint_reset_desiccant(device):
    """Get the endpoint for the device"""
    if device.device_type == FEEDER_MINI:
        return PetkitEndpoint.MINI_DESICCANT_RESET
    if device.device_type == FEEDER:
        return PetkitEndpoint.FRESH_ELEMENT_DESICCANT_RESET
    return PetkitEndpoint.DESICCANT_RESET


ACTIONS_MAP = {
    DeviceCommand.UPDATE_SETTING: CmdData(
        endpoint=PetkitEndpoint.UPDATE_SETTING,
        params=lambda device, setting: {
            "id": device.id,
            "kv": json.dumps(setting),
        },
        supported_device=ALL_DEVICES,
    ),
    FeederCommand.MANUAL_FEED: CmdData(
        endpoint=lambda device: get_endpoint_manual_feed(device),
        params=lambda device, setting: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            "time": "-1",
            **setting,
        },
        supported_device=DEVICES_FEEDER,  # TODO: Check if this is correct
    ),
    FeederCommand.MANUAL_FEED_DUAL: CmdData(
        endpoint=PetkitEndpoint.UPDATE_SETTING,
        params=lambda device, setting: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            "name": "",
            "time": "-1",
            **setting,
        },
        supported_device=ALL_DEVICES,
    ),
    FeederCommand.CANCEL_MANUAL_FEED: CmdData(
        endpoint=lambda device: (
            PetkitEndpoint.FRESH_ELEMENT_CANCEL_FEED
            if device.device_type == FEEDER
            else PetkitEndpoint.CANCEL_FEED
        ),
        params=lambda device: {
            "day": datetime.datetime.now().strftime("%Y%m%d"),
            "deviceId": device.id,
            **(
                {"id": device.manual_feed_id}
                if device.device_type.lower() in [D4H, D4S, D4SH]
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
    # TODO : Find how to support power ON/OFF
    LitterCommand.CONTROL_DEVICE: CmdData(
        endpoint=PetkitEndpoint.CONTROL_DEVICE,
        params=lambda device, command: {
            "id": device.id,
            "kv": json.dumps({LB_CMD_TO_KEY[command]: LB_CMD_TO_VALUE[command]}),
            "type": LB_CMD_TO_TYPE[command],
        },
        supported_device=[T3, T4, T5, T6],
    ),
    # TODO : Find how to support Pet Setting with send_api_request
    # PetCommand.UPDATE_SETTING: CmdData(
    #     endpoint=PetkitEndpoint.CONTROL_DEVICE,
    #     params=lambda pet, setting: {
    #         "petId": pet,
    #         "kv": json.dumps(setting),
    #     },
    #     supported_device=ALL_DEVICES,
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
