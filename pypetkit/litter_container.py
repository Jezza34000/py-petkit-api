"""Dataclasses for Litter."""

from dataclasses import dataclass

from pypetkit.const import PetkitEndpoint
from pypetkit.containers import CloudProduct, FirmwareDetail, PetkitBase, Wifi


@dataclass
class SettingsLitter(PetkitBase):
    """Dataclass for settings.
    -> LitterData subclass.
    """

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
    """Dataclass for state.
    -> LitterData subclass.
    """

    box: int | None = None
    box_full: bool | None = None
    box_state: int | None = None
    deodorant_left_days: int | None = None
    frequent_restroom: int | None = None
    liquid_empty: bool | None = None
    liquid_lack: bool | None = None
    liquid_reset: int | None = None
    low_power: bool | None = None
    offline_time: int | None = None
    ota: int | None = None
    overall: int | None = None
    pet_error: bool | None = None
    pet_in_time: int | None = None
    pim: int | None = None
    power: int | None = None
    sand_correct: int | None = None
    sand_lack: bool | None = None
    sand_percent: int | None = None
    sand_status: int | None = None
    sand_type: int | None = None
    sand_weight: int | None = None
    used_times: int | None = None
    wifi: Wifi | None = None
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
class Litter(PetkitBase):
    """Dataclass for Litter Data.
    Supported devices = T4, T6
    """

    _ignore_keys = ["user", "special_litter_ad"]
    query_param = {"id": None}

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint for the device type."""
        return PetkitEndpoint.DEVICE_DETAIL

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
    pet_out_tips: list[any]
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
    device_type: str | None = None
