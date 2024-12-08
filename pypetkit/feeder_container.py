"""Dataclasses for Feeders."""

from dataclasses import dataclass

from pypetkit.const import PetkitEndpoint
from pypetkit.containers import CloudProduct, FirmwareDetail, PetkitBase, Wifi


@dataclass
class FeedItem(PetkitBase):
    """Dataclass for PetKit Feeders.
    -> FeedDailyList subclass.
    """

    id: str | None = None
    name: str | None = None
    time: int | None = None
    amount: int | None = None  # For D4H
    amount1: int | None = None  # For D4SH
    amount2: int | None = None  # For D4SH


@dataclass
class FeedDailyList(PetkitBase):
    """Dataclass for PetKit Feeders.
    -> MultiFeedItem subclass.
    """

    items: list[FeedItem] | None = None
    repeats: int | None = None
    suspended: int | None = None


@dataclass
class MultiFeedItem(PetkitBase):
    """Dataclass for PetKit Feeders.
    -> FeederData subclass.
    """

    feed_daily_list: list[FeedDailyList] | None = None
    is_executed: int | None = None
    user_id: str | None = None


@dataclass
class CameraMultiNew(PetkitBase):
    """Dataclass for PetKit Feeders.
    -> SettingsFeeder subclass.
    """

    enable: int | None = None
    rpt: str | None = None
    time: list[tuple[int, int]] | None = None


@dataclass
class SettingsFeeder(PetkitBase):
    """Dataclass for PetKit Feeders
    -> FeederData subclass.
    """

    attire_id: int | None = None
    attire_switch: int | None = None
    auto_product: int | None = None
    camera: int | None = None
    camera_config: int | None = None
    camera_multi_range: list | None = None
    control_settings: int | None = None
    desiccant_notify: int | None = None
    detect_config: int | None = None
    detect_interval: int | None = None
    detect_multi_range: list | None = None
    eat_detection: int | None = None
    eat_notify: int | None = None
    eat_sensitivity: int | None = None
    eat_video: int | None = None
    feed_notify: int | None = None
    feed_picture: int | None = None
    food_notify: int | None = None
    food_warn: int | None = None
    food_warn_range: list[int] | None = None
    highlight: int | None = None
    light_config: int | None = None
    light_mode: int | None = None
    light_multi_range: list[tuple[int, int]] | None = None
    live_encrypt: int | None = None
    low_battery_notify: int | None = None
    manual_lock: int | None = None
    microphone: int | None = None
    move_detection: int | None = None
    move_notify: int | None = None
    move_sensitivity: int | None = None
    night: int | None = None
    num_limit: int | None = None
    pet_detection: int | None = None
    pet_notify: int | None = None
    pet_sensitivity: int | None = None
    pre_live: int | None = None
    selected_sound: int | None = None
    smart_frame: int | None = None
    sound_enable: int | None = None
    surplus_control: int | None = None
    surplus_standard: int | None = None
    system_sound_enable: int | None = None
    time_display: int | None = None
    tone_config: int | None = None
    tone_mode: int | None = None
    tone_multi_range: list[tuple[int, int]] | None = None
    upload: int | None = None
    volume: int | None = None
    feed_sound: int | None = None  # For D4H
    factor: int | None = None  # For D4H
    color_setting: int | None = None  # For D4H
    conservation: int | None = None  # For D4SH
    bucket_name1: str | None = None  # For D4SH
    bucket_name2: str | None = None  # For D4SH
    camera_multi_new: list[CameraMultiNew] | None = None  # For D4SH


@dataclass
class FeedState(PetkitBase):
    """Dataclass for PetKit Feeders.
    -> StateFeeder subclass.
    """

    eat_avg: int | None = None
    eat_count: int | None = None
    eat_times: list[int] | None = None
    feed_times: dict | None = None
    times: int | None = None
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
    """Dataclass for PetKit Feeders.
    -> FeederData subclass.
    """

    battery_power: int | None = None
    battery_status: int | None = None
    bowl: int | None = None
    camera_status: int | None = None
    desiccant_left_days: int | None = None
    desiccant_time: int | None = None
    door: int | None = None
    feed_state: FeedState | None = None
    feeding: int | None = None
    ota: int | None = None
    overall: int | None = None
    pim: int | None = None
    runtime: int | None = None
    wifi: Wifi | None = None
    eating: int | None = None  # For D4SH
    food: int | None = None  # For D4H
    food1: int | None = None  # For D4SH
    food2: int | None = None  # For D4SH
    conservation_status: int | None = None  # For D4SH


@dataclass
class Feeder(PetkitBase):
    """Dataclass for PetKit Feeders.
    Supported devices = D4H, D4SH
    """

    _ignore_keys = ["user", "freeCareInfo"]
    query_param = {"id": None}

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint for the device type."""
        return PetkitEndpoint.DEVICE_DETAIL

    auto_upgrade: int | None = None
    bt_mac: str | None = None
    cloud_product: CloudProduct | None = None
    created_at: str | None = None
    firmware: str | None = None
    firmware_details: list[FirmwareDetail] | None = None
    hardware: int | None = None
    id: int | None = None
    locale: str | None = None
    mac: str | None = None
    model_code: int | None = None
    multi_feed_item: MultiFeedItem | None = None
    name: str | None = None
    secret: str | None = None
    service_status: int | None = None
    settings: SettingsFeeder | None = None
    share_open: int | None = None
    signup_at: str | None = None
    sn: str | None = None
    state: StateFeeder | None = None
    timezone: float | None = None
    p2p_type: int | None = None  # For D4H
    multi_config: bool | None = None  # For D4H
    device_type: str | None = None


@dataclass
class EventState(PetkitBase):
    """Dataclass for storing event state.
    -> FeederEventData subclass.
    """

    completed_at: str | None = None
    err_code: int | None = None
    media: int | None = None
    real_amount1: int | None = None
    real_amount2: int | None = None
    result: int | None = None
    surplus_standard: int | None = None


@dataclass
class FeederRecord(PetkitBase):
    """Dataclass for storing event data."""

    aes_key: str | None = None
    duration: int | None = None
    event_id: str | None = None
    expire: int | None = None
    mark: int | None = None
    media_api: str | None = None
    start_time: int | None = None
    storage_space: int | None = None
    eat_video: int | None = None
    is_need_upload_video: int | None = None
    preview: str | None = None
    time: int | None = None
    timestamp: int | None = None
    aes_key1: str | None = None
    aes_key2: str | None = None
    amount1: int | None = None
    amount2: int | None = None
    completed_at: int | None = None
    content: dict[str, any] | None = None
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
