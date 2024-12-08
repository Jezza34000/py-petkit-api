"""Pypet containers for data storage and management."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import asdict, dataclass
from enum import Enum
import logging
import re
from typing import Any, ClassVar, get_args, get_origin

_LOGGER = logging.getLogger(__name__)


def camelize(s: str) -> str:
    """Convert camelCase to snake_case."""
    first, *others = s.split("_")
    if len(others) == 0:
        return s
    return "".join([first.lower(), *map(str.title, others)])


def decamelize(s: str) -> str:
    """Convert snake_case to camelCase."""
    return re.sub("([A-Z]+)", "_\\1", s).lower()


def decamelize_obj(d: dict | list, ignore_keys: list[str]) -> dict | list:
    """Convert camelCase to snake_case for all keys in a dict or list of dicts."""
    if isinstance(d, PetkitBase):
        d = d.as_dict()
    if isinstance(d, list):
        return [
            decamelize_obj(i, ignore_keys) if isinstance(i, dict | list) else i
            for i in d
        ]
    return {
        (decamelize(a) if a not in ignore_keys else a): (
            decamelize_obj(b, ignore_keys) if isinstance(b, dict | list) else b
        )
        for a, b in d.items()
    }


@dataclass
class PetkitBase:
    """Base class for all Petkit data classes."""

    _ignore_keys: ClassVar[list[str]] = []
    is_cached = False

    @staticmethod
    def convert_to_class_obj(type_d, value):
        """Convert a value to a class object."""
        try:
            class_type = eval(type_d)  # noqa: S307
            if get_origin(class_type) is list:
                return_list = []
                cls_type = get_args(class_type)[0]
                for obj in value:
                    if issubclass(cls_type, PetkitBase):
                        return_list.append(cls_type.from_dict(obj))
                    elif cls_type in {str, int, float}:
                        return_list.append(cls_type(obj))
                    else:
                        return_list.append(cls_type(**obj))
                return return_list
            if issubclass(class_type, PetkitBase):
                converted_value = class_type.from_dict(value)
            else:
                converted_value = class_type(value)
            return converted_value  # noqa: TRY300
        except Exception:  # noqa: TRY203
            raise

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Convert a dictionary to a dataclass object."""
        if isinstance(data, dict):
            ignore_keys = cls._ignore_keys
            data = decamelize_obj(data, ignore_keys)
            cls_annotations: dict[str, str] = {}
            for base in reversed(cls.__mro__):
                cls_annotations.update(getattr(base, "__annotations__", {}))
            remove_keys = []
            for key, value in data.items():
                if value == "None" or value is None:
                    data[key] = None
                    continue
                if key not in cls_annotations:
                    remove_keys.append(key)
                    continue
                field_type: str = cls_annotations[key]
                if "|" in field_type:
                    # It's a union
                    types = field_type.split("|")
                    for vtype in types:
                        if "None" in vtype or "Any" in vtype:
                            continue
                        with suppress(Exception):
                            data[key] = PetkitBase.convert_to_class_obj(vtype, value)
                            break
                else:
                    with suppress(Exception):
                        data[key] = PetkitBase.convert_to_class_obj(field_type, value)
            for key in remove_keys:
                del data[key]
            return cls(**data)
        return None

    def as_dict(self) -> dict:
        """Convert a dataclass object to a dictionary."""
        return asdict(
            self,
            dict_factory=lambda _fields: {
                camelize(key): value.value if isinstance(value, Enum) else value
                for (key, value) in _fields
                if value is not None
            },
        )


# ====================================================================================================
# DataClass used for account
# ====================================================================================================


@dataclass
class RegionInfo(PetkitBase):
    """Dataclass for region data."""

    account_type: str | None = None
    gateway: str | None = None
    id: str | None = None
    name: str | None = None


@dataclass
class SessionInfo(PetkitBase):
    """Dataclass for session data."""

    id: str | None = None
    user_id: str | None = None
    expires_in: int | None = None
    region: str | None = None
    created_at: str | None = None


@dataclass
class Device(PetkitBase):
    """Dataclass for device data."""

    created_at: int | None = None
    device_id: int | None = None
    device_name: str | None = None
    device_type: str | None = None
    group_id: int | None = None
    type: int | None = None
    type_code: int | None = None
    unique_id: str | None = None


@dataclass
class Pet(PetkitBase):
    """Dataclass for pet data."""

    avatar: str | None = None
    created_at: int | None = None
    pet_id: int | None = None
    pet_name: str | None = None


@dataclass
class User(PetkitBase):
    """Dataclass for user data."""

    avatar: str | None = None
    created_at: int | None = None
    is_owner: int | None = None
    user_id: int | None = None
    user_name: str | None = None


@dataclass
class AccountData(PetkitBase):
    """Dataclass for account data."""

    device_list: list[Device] | None = None
    expired: bool | None = None
    group_id: int | None = None
    name: str | None = None
    owner: int | None = None
    pet_list: list[Pet] | None = None
    user_list: list[User] | None = None


# ====================================================================================================
# DataClass used by many devices
# ====================================================================================================


@dataclass
class CloudProduct(PetkitBase):
    """Dataclass for cloud product details.
    Care+ Service for Smart devices with Camera.
    """

    charge_type: str | None = None
    name: str | None = None
    service_id: int | None = None
    subscribe: int | None = None
    work_indate: int | None = None
    work_time: int | None = None


@dataclass
class Wifi(PetkitBase):
    """Dataclass for Wi-Fi."""

    bssid: str | None = None
    rsq: int | None = None
    ssid: str | None = None


@dataclass
class FirmwareDetail(PetkitBase):
    """Dataclass for firmware details."""

    module: str | None = None
    version: int | None = None
