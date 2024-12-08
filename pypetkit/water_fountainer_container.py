"""Dataclasses for Water Fountain."""

from dataclasses import dataclass

from pypetkit.const import PetkitEndpoint
from pypetkit.containers import PetkitBase


@dataclass
class Electricity(PetkitBase):
    """Dataclass for electricity details.
    -> WaterFountainData subclass.
    """

    battery_percent: int | None = None
    battery_voltage: int | None = None
    supply_voltage: int | None = None


@dataclass
class Type(PetkitBase):
    """Dataclass for type details.
    -> WaterFountainData subclass.
    """

    enable: int | None = None
    id: str | None = None
    img: str | None = None
    is_custom: int | None = None
    name: str | None = None
    priority: int | None = None
    with_device_type: str | None = None
    with_pet: int | None = None


@dataclass
class Schedule(PetkitBase):
    """Dataclass for schedule details.
    -> WaterFountainData subclass.
    """

    alarm_before: int | None = None
    created_at: str | None = None
    device_id: str | None = None
    device_type: str | None = None
    id: str | None = None
    name: str | None = None
    repeat: str | None = None
    status: int | None = None
    time: str | None = None
    type: Type | None = None
    user_custom_id: int | None = None


@dataclass
class SettingsFountain(PetkitBase):
    """Dataclass for settings.
    -> WaterFountainData subclass.
    """

    battery_sleep_time: int | None = None
    battery_working_time: int | None = None
    distribution_diagram: int | None = None
    disturb_config: int | None = None
    disturb_multi_time: list[dict[str, any]] | None = None
    lamp_ring_brightness: int | None = None
    lamp_ring_switch: int | None = None
    light_config: int | None = None
    light_multi_time: list[dict[str, any]] | None = None
    no_disturbing_switch: int | None = None
    smart_sleep_time: int | None = None
    smart_working_time: int | None = None


@dataclass
class Status(PetkitBase):
    """Dataclass for status details.
    -> WaterFountainData subclass.
    """

    detect_status: int | None = None
    electric_status: int | None = None
    power_status: int | None = None
    run_status: int | None = None
    suspend_status: int | None = None


@dataclass
class WaterFountain(PetkitBase):
    """Dataclass for Water Fountain Data.
    Supported devices = CTW3
    """

    # _ignore_keys = []
    query_param = {"id": None}

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint for the device type."""
        return PetkitEndpoint.DEVICE_DATA

    breakdown_warning: int | None = None
    created_at: str | None = None
    electricity: Electricity | None = None
    expected_clean_water: int | None = None
    expected_use_electricity: float | None = None
    filter_expected_days: int | None = None
    filter_percent: int | None = None
    filter_warning: int | None = None
    firmware: int | None = None
    hardware: int | None = None
    id: int | None = None
    is_night_no_disturbing: int | None = None
    lack_warning: int | None = None
    locale: str | None = None
    low_battery: int | None = None
    mac: str | None = None
    mode: int | None = None
    module_status: int | None = None
    name: str | None = None
    record_automatic_add_water: int | None = None
    schedule: Schedule | None = None
    secret: str | None = None
    settings: SettingsFountain | None = None
    sn: str | None = None
    status: Status | None = None
    sync_time: str | None = None
    timezone: float | None = None
    today_clean_water: int | None = None
    today_pump_run_time: int | None = None
    today_use_electricity: float | None = None
    update_at: str | None = None
    user_id: str | None = None
    water_pump_run_time: int | None = None
    device_type: str | None = None
