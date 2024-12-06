"""Pypet containers for data storage and management."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import asdict, dataclass
from enum import Enum
import logging
import re
from typing import Any, ClassVar, get_args, get_origin

from pypetkit.const import PetkitEndpoint

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


@dataclass
class RegionInfo(PetkitBase):
    """Dataclass for region data."""

    account_type: str
    gateway: str
    id: str
    name: str


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

    created_at: int
    device_id: int
    device_name: str
    device_type: str
    group_id: int
    type: int
    type_code: int
    unique_id: str


@dataclass
class Pet(PetkitBase):
    """Dataclass for pet data."""

    avatar: str
    created_at: int
    pet_id: int
    pet_name: str


@dataclass
class User(PetkitBase):
    """Dataclass for user data."""

    avatar: str
    created_at: int
    is_owner: int
    user_id: int
    user_name: str


@dataclass
class AccountData(PetkitBase):
    """Dataclass for account data."""

    device_list: list[Device]
    expired: bool
    group_id: int
    name: str
    owner: int
    pet_list: list[Pet]
    user_list: list[User]


# ====================================================================================================
# Data classes for many devices
# ====================================================================================================


@dataclass
class CloudProduct(PetkitBase):
    """Dataclass for cloud product details.
    Care+ Service for Smart devices with Camera.
    """

    charge_type: str
    name: str
    service_id: int
    subscribe: int
    work_indate: int
    work_time: int


@dataclass
class Wifi(PetkitBase):
    """Dataclass for Wi-Fi."""

    bssid: str
    rsq: int
    ssid: str


@dataclass
class FirmwareDetail(PetkitBase):
    """Dataclass for firmware details."""

    module: str
    version: int


# ====================================================================================================
# Feeder data classes
# ====================================================================================================


@dataclass
class FeedItem(PetkitBase):
    """Dataclass for PetKit Feeders."""

    id: str
    name: str
    time: int
    amount: int | None = None  # For D4H
    amount1: int | None = None  # For D4SH
    amount2: int | None = None  # For D4SH


@dataclass
class FeedDailyList(PetkitBase):
    """Dataclass for PetKit Feeders."""

    items: list[FeedItem]
    repeats: int
    suspended: int


@dataclass
class MultiFeedItem(PetkitBase):
    """Dataclass for PetKit Feeders."""

    feed_daily_list: list[FeedDailyList]
    is_executed: int
    user_id: str


@dataclass
class CameraMultiNew(PetkitBase):
    """Dataclass for PetKit Feeders."""

    enable: int
    rpt: str
    time: list[tuple[int, int]]


@dataclass
class SettingsFeeder(PetkitBase):
    """Dataclass for PetKit Feeders"""

    attire_id: int
    attire_switch: int
    auto_product: int
    camera: int
    camera_config: int
    camera_multi_range: list
    control_settings: int
    desiccant_notify: int
    detect_config: int
    detect_interval: int
    detect_multi_range: list
    eat_detection: int
    eat_notify: int
    eat_sensitivity: int
    eat_video: int
    feed_notify: int
    feed_picture: int
    food_notify: int
    food_warn: int
    food_warn_range: list[int]
    highlight: int
    light_config: int
    light_mode: int
    light_multi_range: list[tuple[int, int]]
    live_encrypt: int
    low_battery_notify: int
    manual_lock: int
    microphone: int
    move_detection: int
    move_notify: int
    move_sensitivity: int
    night: int
    num_limit: int
    pet_detection: int
    pet_notify: int
    pet_sensitivity: int
    pre_live: int
    selected_sound: int
    smart_frame: int
    sound_enable: int
    surplus_control: int
    surplus_standard: int
    system_sound_enable: int
    time_display: int
    tone_config: int
    tone_mode: int
    tone_multi_range: list[tuple[int, int]]
    upload: int
    volume: int

    feed_sound: int | None = None  # For D4H
    factor: int | None = None  # For D4H
    color_setting: int | None = None  # For D4H

    conservation: int | None = None  # For D4SH
    bucket_name1: str | None = None  # For D4SH
    bucket_name2: str | None = None  # For D4SH
    camera_multi_new: list[CameraMultiNew] | None = None  # For D4SH


@dataclass
class FeedState(PetkitBase):
    """Dataclass for PetKit Feeders."""

    eat_avg: int
    eat_count: int
    eat_times: list[int]
    feed_times: dict
    times: int

    add_amount_total: int | None = None  # For D4H
    plan_amount_total: int | None = None  # For D4H
    plan_real_amount_total: int | None = None  # For D4H
    real_amount_total: int | None = None  # For D4H

    add_amount_total1: int | None = None  # For D4SH
    add_amount_total2: int | None = None  # For D4SH
    plan_amount_total1: int | None = None  # For D4SH
    plan_amount_total2: int | None = None  # For D4SH
    plan_real_amount_total1: int | None = None  # For D4SH
    plan_real_amount_total2: int | None = None  # For D4SH
    real_amount_total1: int | None = None  # For D4SH
    real_amount_total2: int | None = None  # For D4SH


@dataclass
class StateFeeder(PetkitBase):
    """Dataclass for PetKit Feeders."""

    battery_power: int
    battery_status: int
    bowl: int
    camera_status: int
    desiccant_left_days: int
    desiccant_time: int
    door: int
    feed_state: FeedState
    feeding: int
    ota: int
    overall: int
    pim: int
    runtime: int
    wifi: Wifi
    eating: int | None = None  # For D4SH
    food: int | None = None  # For D4H
    food1: int | None = None  # For D4SH
    food2: int | None = None  # For D4SH
    conservation_status: int | None = None  # For D4SH


@dataclass
class FeederData(PetkitBase):
    """Dataclass for PetKit Feeders.
    Supported devices = D4H, D4SH
    """

    _ignore_keys = ["user", "freeCareInfo"]
    url_endpoint = PetkitEndpoint.DEVICE_DETAIL
    query_param = {"id": None}

    auto_upgrade: int
    bt_mac: str
    cloud_product: CloudProduct
    created_at: str
    firmware: str
    firmware_details: list[FirmwareDetail]
    hardware: int
    id: int
    locale: str
    mac: str
    model_code: int
    multi_feed_item: MultiFeedItem
    name: str
    secret: str
    service_status: int
    settings: SettingsFeeder
    share_open: int
    signup_at: str
    sn: str
    state: StateFeeder
    timezone: float
    p2p_type: int | None = None  # For D4H
    multi_config: bool | None = None  # For D4H


@dataclass
class EventState(PetkitBase):
    """Dataclass for storing event state."""

    completed_at: str | None = None
    err_code: int | None = None
    media: int | None = None
    real_amount1: int | None = None
    real_amount2: int | None = None
    result: int | None = None
    surplus_standard: int | None = None


@dataclass
class FeederEventData(PetkitBase):
    """Dataclass for storing event data."""

    aes_key: str
    duration: int
    event_id: str
    expire: int
    mark: int
    media_api: str
    start_time: int
    storage_space: int
    eat_video: int
    is_need_upload_video: int
    preview: str
    time: int | None = None
    timestamp: int | None = None
    aes_key1: str | None = None
    aes_key2: str | None = None
    amount1: int | None = None
    amount2: int | None = None
    completed_at: int | None = None
    content: dict[str, Any] | None = None
    desc: str | None = None
    device_id: int | None = None
    eat_end_time: int | None = None
    eat_start_time: int | None = None
    empty: int | None = None
    end_time: int | None = None
    enum_event_type: str | None = None
    event: str | None = None
    event_type: int | None = None
    expire1: int | None = None
    expire2: int | None = None
    id: str | None = None
    is_executed: int | None = None
    media_list: list[any] | None = None
    name: str | None = None
    preview1: str | None = None
    preview2: str | None = None
    src: int | None = None
    state: EventState | None = None
    status: int | None = None


# ====================================================================================================
# Litter data classes
# ====================================================================================================


@dataclass
class SettingsLitter(PetkitBase):
    """Dataclass for settings."""

    auto_interval_min: int
    auto_work: int
    avoid_repeat: int
    bury: int
    control_settings: int
    deep_clean: int
    deep_refresh: int
    deodorant_notify: int
    distrub_multi_range: list[list[int]]
    disturb_config: int
    disturb_mode: int
    disturb_range: list[int]
    downpos: int
    dump_switch: int
    fixed_time_clear: int
    kitten: int
    kitten_percent: float
    kitten_tips_time: int
    lack_liquid_notify: int
    lack_sand_notify: int
    language: str
    language_follow: int
    languages: list[str]
    light_config: int
    light_mode: int
    light_multi_range: list[any]
    light_range: list[int]
    lightest: int
    litter_full_notify: int
    manual_lock: int
    pet_in_notify: int
    relate_k3_switch: int
    sand_type: int
    soft_mode: int
    still_time: int
    stop_time: int
    underweight: int
    unit: int
    weight_popup: int
    work_notify: int
    auto_product: int | None = None
    camera: int | None = None
    camera_config: int | None = None
    cleanning_notify: int | None = None
    garbage_notify: int | None = None
    highlight: int | None = None
    light_assist: int | None = None
    live_encrypt: int | None = None
    microphone: int | None = None
    move_notify: int | None = None
    night: int | None = None
    package_standard: list[int] | None = None
    pet_detection: int | None = None
    pet_notify: int | None = None
    pre_live: int | None = None
    system_sound_enable: int | None = None
    time_display: int | None = None
    toilet_detection: int | None = None
    toilet_notify: int | None = None
    tone_config: int | None = None
    tone_mode: int | None = None
    tone_multi_range: list[list[int]] | None = None
    tumbling: int | None = None
    upload: int | None = None
    volume: int | None = None
    wander_detection: int | None = None


@dataclass
class StateLitter(PetkitBase):
    """Dataclass for state."""

    box: int
    box_full: bool
    box_state: int
    deodorant_left_days: int
    frequent_restroom: int
    liquid_empty: bool
    liquid_lack: bool
    liquid_reset: int
    low_power: bool
    offline_time: int
    ota: int
    overall: int
    pet_error: bool
    pet_in_time: int
    pim: int
    power: int
    sand_correct: int
    sand_lack: bool
    sand_percent: int
    sand_status: int
    sand_type: int
    sand_weight: int
    used_times: int
    wifi: Wifi
    bagging_state: int | None = None
    battery: int | None = None
    box_store_state: int | None = None
    camera_status: int | None = None
    dump_state: int | None = None
    liquid: int | None = None
    pack_state: int | None = None
    package_install: int | None = None
    package_secret: str | None = None
    package_sn: str | None = None
    package_state: int | None = None
    pi_ins: int | None = None
    purification_left_days: int | None = None
    seal_door_state: int | None = None
    top_ins: int | None = None
    wander_time: int | None = None


@dataclass
class LitterData(PetkitBase):
    """Dataclass for Litter Data.
    Supported devices = T4, T6
    """

    _ignore_keys = ["user", "special_litter_ad"]
    url_endpoint = PetkitEndpoint.DEVICE_DETAIL
    query_param = {"id": None}

    auto_upgrade: int
    bt_mac: str
    created_at: str
    firmware: str
    firmware_details: list[FirmwareDetail]
    hardware: int
    id: int
    is_pet_out_tips: int
    locale: str
    mac: str
    maintenance_time: int
    multi_config: bool
    name: str
    pet_in_tip_limit: int
    pet_out_tips: list[Any]
    secret: str
    settings: SettingsLitter
    share_open: int
    signup_at: str
    sn: str
    state: StateLitter
    timezone: float
    cloud_product: CloudProduct | None = None  # For T5/T6
    in_times: int | None = None
    last_out_time: int | None = None
    p2p_type: int | None = None
    package_ignore_state: int | None = None
    package_total_count: int | None = None
    package_used_count: int | None = None
    pet_out_records: list[list[int]] | None = None
    service_status: int | None = None
    total_time: int | None = None


# ====================================================================================================
# Water Fountain data classes
# ====================================================================================================


@dataclass
class Electricity(PetkitBase):
    """Dataclass for electricity details."""

    battery_percent: int
    battery_voltage: int
    supply_voltage: int


@dataclass
class Type(PetkitBase):
    """Dataclass for type details."""

    enable: int
    id: str
    img: str
    is_custom: int
    name: str
    priority: int
    with_device_type: str
    with_pet: int


@dataclass
class Schedule(PetkitBase):
    """Dataclass for schedule details."""

    alarm_before: int
    created_at: str
    device_id: str
    device_type: str
    id: str
    name: str
    repeat: str
    status: int
    time: str
    type: Type
    user_custom_id: int


@dataclass
class SettingsFountain(PetkitBase):
    """Dataclass for settings."""

    battery_sleep_time: int
    battery_working_time: int
    distribution_diagram: int
    disturb_config: int
    disturb_multi_time: list[dict[str, Any]]
    lamp_ring_brightness: int
    lamp_ring_switch: int
    light_config: int
    light_multi_time: list[dict[str, Any]]
    no_disturbing_switch: int
    smart_sleep_time: int
    smart_working_time: int


@dataclass
class Status(PetkitBase):
    """Dataclass for status details."""

    detect_status: int
    electric_status: int
    power_status: int
    run_status: int
    suspend_status: int


@dataclass
class WaterFountainData(PetkitBase):
    """Dataclass for Water Fountain Data.
    Supported devices = CTW3
    """

    # _ignore_keys = []
    url_endpoint = PetkitEndpoint.DEVICE_DATA
    query_param = {"id": None}

    breakdown_warning: int
    created_at: str
    electricity: Electricity
    expected_clean_water: int
    expected_use_electricity: float
    filter_expected_days: int
    filter_percent: int
    filter_warning: int
    firmware: int
    hardware: int
    id: int
    is_night_no_disturbing: int
    lack_warning: int
    locale: str
    low_battery: int
    mac: str
    mode: int
    module_status: int
    name: str
    record_automatic_add_water: int
    schedule: Schedule
    secret: str
    settings: SettingsFountain
    sn: str
    status: Status
    sync_time: str
    timezone: float
    today_clean_water: int
    today_pump_run_time: int
    today_use_electricity: float
    update_at: str
    user_id: str
    water_pump_run_time: int
