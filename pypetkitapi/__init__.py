"""Pypetkit: A Python library for interfacing with PetKit"""

from .client import PetKitClient
from .command import FeederCommand, LBAction, LBCommand, LitterCommand, PetCommand
from .const import (
    CTW3,
    D3,
    D4,
    D4H,
    D4S,
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
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
from .medias import MediaHandler, MediasFiles

__version__ = "1.7.10"

__all__ = [
    "MediasFiles",
    "MediaHandler",
    "D3",
    "D4",
    "D4H",
    "D4S",
    "FEEDER",
    "FEEDER_MINI",
    "T3",
    "T4",
    "T5",
    "T6",
    "W5",
    "CTW3",
    "K2",
    "K3",
    "DEVICES_FEEDER",
    "DEVICES_LITTER_BOX",
    "DEVICES_WATER_FOUNTAIN",
    "RecordType",
    "PetKitClient",
    "FeederCommand",
    "LitterCommand",
    "PetCommand",
    "LBCommand",
    "LBAction",
]
