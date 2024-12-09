"""Dataclasses for Water Fountain."""

from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import PetkitEndpoint


class Electricity(BaseModel):
    """Dataclass for electricity details.
    -> WaterFountainData subclass.
    """

    battery_percent: int | None = Field(None, alias="batteryPercent")
    battery_voltage: int | None = Field(None, alias="batteryVoltage")
    supply_voltage: int | None = Field(None, alias="supplyVoltage")


class Type(BaseModel):
    """Dataclass for type details.
    -> WaterFountainData subclass.
    """

    enable: int | None = None
    id: str | None = None
    img: str | None = None
    is_custom: int | None = Field(None, alias="isCustom")
    name: str | None = None
    priority: int | None = None
    with_device_type: str | None = Field(None, alias="withDeviceType")
    with_pet: int | None = Field(None, alias="withPet")


class Schedule(BaseModel):
    """Dataclass for schedule details.
    -> WaterFountainData subclass.
    """

    alarm_before: int | None = Field(None, alias="alarmBefore")
    created_at: str | None = Field(None, alias="createdAt")
    device_id: str | None = Field(None, alias="deviceId")
    device_type: str | None = Field(None, alias="deviceType")
    id: str | None = None
    name: str | None = None
    repeat: str | None = None
    status: int | None = None
    time: str | None = None
    type: Type | None = None
    user_custom_id: int | None = Field(None, alias="userCustomId")


class SettingsFountain(BaseModel):
    """Dataclass for settings.
    -> WaterFountainData subclass.
    """

    battery_sleep_time: int | None = Field(None, alias="batterySleepTime")
    battery_working_time: int | None = Field(None, alias="batteryWorkingTime")
    distribution_diagram: int | None = Field(None, alias="distributionDiagram")
    disturb_config: int | None = Field(None, alias="disturbConfig")
    disturb_multi_time: list[dict[str, Any]] | None = Field(
        None, alias="disturbMultiTime"
    )
    lamp_ring_brightness: int | None = Field(None, alias="lampRingBrightness")
    lamp_ring_switch: int | None = Field(None, alias="lampRingSwitch")
    light_config: int | None = Field(None, alias="lightConfig")
    light_multi_time: list[dict[str, Any]] | None = Field(None, alias="lightMultiTime")
    no_disturbing_switch: int | None = Field(None, alias="noDisturbingSwitch")
    smart_sleep_time: int | None = Field(None, alias="smartSleepTime")
    smart_working_time: int | None = Field(None, alias="smartWorkingTime")


class Status(BaseModel):
    """Dataclass for status details.
    -> WaterFountainData subclass.
    """

    detect_status: int | None = Field(None, alias="detectStatus")
    electric_status: int | None = Field(None, alias="electricStatus")
    power_status: int | None = Field(None, alias="powerStatus")
    run_status: int | None = Field(None, alias="runStatus")
    suspend_status: int | None = Field(None, alias="suspendStatus")


class WaterFountain(BaseModel):
    """Dataclass for Water Fountain Data.
    Supported devices = CTW3
    """

    url_endpoint: ClassVar[PetkitEndpoint] = PetkitEndpoint.DEVICE_DATA
    query_param: ClassVar[Callable] = lambda device_id: {"id": device_id}

    breakdown_warning: int | None = Field(None, alias="breakdownWarning")
    created_at: str | None = Field(None, alias="createdAt")
    electricity: Electricity | None = None
    expected_clean_water: int | None = Field(None, alias="expectedCleanWater")
    expected_use_electricity: float | None = Field(None, alias="expectedUseElectricity")
    filter_expected_days: int | None = Field(None, alias="filterExpectedDays")
    filter_percent: int | None = Field(None, alias="filterPercent")
    filter_warning: int | None = Field(None, alias="filterWarning")
    firmware: int | None = None
    hardware: int | None = None
    id: int | None = None
    is_night_no_disturbing: int | None = Field(None, alias="isNightNoDisturbing")
    lack_warning: int | None = Field(None, alias="lackWarning")
    locale: str | None = None
    low_battery: int | None = Field(None, alias="lowBattery")
    mac: str | None = None
    mode: int | None = None
    module_status: int | None = Field(None, alias="moduleStatus")
    name: str | None = None
    record_automatic_add_water: int | None = Field(
        None, alias="recordAutomaticAddWater"
    )
    schedule: Schedule | None = None
    secret: str | None = None
    settings: SettingsFountain | None = None
    sn: str | None = None
    status: Status | None = None
    sync_time: str | None = Field(None, alias="syncTime")
    timezone: float | None = None
    today_clean_water: int | None = Field(None, alias="todayCleanWater")
    today_pump_run_time: int | None = Field(None, alias="todayPumpRunTime")
    today_use_electricity: float | None = Field(None, alias="todayUseElectricity")
    update_at: str | None = Field(None, alias="updateAt")
    user_id: str | None = Field(None, alias="userId")
    water_pump_run_time: int | None = Field(None, alias="waterPumpRunTime")
    device_type: str | None = Field(None, alias="deviceType")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return cls.url_endpoint.value
