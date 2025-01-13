"""Pypetkit: A Python library for interfacing with PetKit"""

from .client import PetKitClient
from .command import (
    DeviceAction,
    DeviceCommand,
    FeederCommand,
    LBCommand,
    LitterCommand,
    PetCommand,
    PurMode,
)
from .const import (
    CTW3,
    D3,
    D4,
    D4H,
    D4S,
    D4SH,
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    DEVICES_PURIFIER,
    DEVICES_WATER_FOUNTAIN,
    FEEDER,
    FEEDER_MINI,
    K2,
    K3,
    T3,
    T4,
    T5,
    T6,
    W5,
    RecordType,
)
from .containers import Pet
from .exceptions import PetkitAuthenticationError, PypetkitError
from .feeder_container import Feeder, RecordsItems
from .litter_container import Litter, LitterRecord, WorkState
from .media import DownloadDecryptMedia, MediaFile, MediaManager
from .purifier_container import Purifier
from .water_fountain_container import WaterFountain

__version__ = "1.9.4"

__all__ = [
    "CTW3",
    "D3",
    "D4",
    "D4H",
    "D4S",
    "D4SH",
    "DEVICES_FEEDER",
    "DEVICES_LITTER_BOX",
    "DEVICES_PURIFIER",
    "DEVICES_WATER_FOUNTAIN",
    "DeviceAction",
    "DeviceCommand",
    "FEEDER",
    "FEEDER_MINI",
    "Feeder",
    "FeederCommand",
    "K2",
    "K3",
    "LBCommand",
    "Litter",
    "LitterCommand",
    "LitterRecord",
    "MediaManager",
    "DownloadDecryptMedia",
    "MediaFile",
    "Pet",
    "PetCommand",
    "PetKitClient",
    "PetkitAuthenticationError",
    "PurMode",
    "Purifier",
    "PypetkitError",
    "RecordType",
    "RecordsItems",
    "T3",
    "T4",
    "T5",
    "T6",
    "W5",
    "WaterFountain",
    "WorkState",
]
