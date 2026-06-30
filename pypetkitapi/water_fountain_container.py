"""Dataclasses for Water Fountain."""

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import CTW3, DEVICE_DATA, DEVICE_RECORDS, W7H, PetkitEndpoint
from pypetkitapi.containers import (
    CloudProduct,
    Device,
    FirmwareDetail,
    LiveFeed,
    UserDevice,
    Wifi,
)


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
    Supports both CTW3 and EVERSWEET ULTRA AI (W4).
    """

    # Ble fountains fields
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

    # EVERSWEET ULTRA AI (W4) fields
    manual_lock: int | None = Field(None, alias="manualLock")
    click_ok_enable: int | None = Field(None, alias="clickOkEnable")
    language: str | None = None
    languages: list[str] | None = None
    disturb_mode: int | None = Field(None, alias="disturbMode")
    distrub_multi_range: list[list[int]] | None = Field(None, alias="distrubMultiRange")
    camera: int | None = None
    camera_config: int | None = Field(None, alias="cameraConfig")
    microphone: int | None = None
    night: int | None = None
    time_display: int | None = Field(None, alias="timeDisplay")
    camera_light: int | None = Field(None, alias="cameraLight")
    micro_light: int | None = Field(None, alias="microLight")
    smart_frame: int | None = Field(None, alias="smartFrame")
    highlight: int | None = None
    auto_product: int | None = Field(None, alias="autoProduct")
    upload: int | None = None
    pre_live: int | None = Field(None, alias="preLive")
    live_encrypt: int | None = Field(None, alias="liveEncrypt")
    pet_detection: int | None = Field(None, alias="petDetection")
    drink_detection: int | None = Field(None, alias="drinkDetection")
    flush_notify: int | None = Field(None, alias="flushNotify")
    water_change_notify: int | None = Field(None, alias="waterChangeNotify")
    clean_water_lack_notify: int | None = Field(None, alias="cleanWaterLackNotify")
    clean_water_empty_notify: int | None = Field(None, alias="cleanWaterEmptyNotify")
    waste_water_full_notify: int | None = Field(None, alias="wasteWaterFullNotify")
    pet_notify: int | None = Field(None, alias="petNotify")
    pet_notify_interval: int | None = Field(None, alias="petNotifyInterval")
    drink_notify: int | None = Field(None, alias="drinkNotify")
    add_water_notify: int | None = Field(None, alias="addWaterNotify")
    light_mode: int | None = Field(None, alias="lightMode")
    light_multi_range: list[list[int]] | None = Field(None, alias="lightMultiRange")
    light_assist: int | None = Field(None, alias="lightAssist")
    tone_mode: int | None = Field(None, alias="toneMode")
    tone_multi_range: list[list[int]] | None = Field(None, alias="toneMultiRange")
    tone_config: int | None = Field(None, alias="toneConfig")
    system_sound_enable: int | None = Field(None, alias="systemSoundEnable")
    volume: int | None = None
    flush_intensity: int | None = Field(None, alias="flushIntensity")
    auto_flush: int | None = Field(None, alias="autoFlush")
    flush_cycle: int | None = Field(None, alias="flushCycle")
    flush_time: int | None = Field(None, alias="flushTime")
    fountain_mode: int | None = Field(None, alias="fountainMode")
    fountain_time: int | None = Field(None, alias="fountainTime")
    sleep_time: int | None = Field(None, alias="sleepTime")
    heater_switch: int | None = Field(None, alias="heaterSwitch")
    heater_temp: int | None = Field(None, alias="heaterTemp")
    auto_water_change: int | None = Field(None, alias="autoWaterChange")
    water_change_cycle: int | None = Field(None, alias="waterChangeCycle")
    water_change_time: int | None = Field(None, alias="waterChangeTime")
    add_water_switch: int | None = Field(None, alias="addWaterSwitch")
    add_water_mode: int | None = Field(None, alias="addWaterMode")
    aw_disturb_mode: int | None = Field(None, alias="awDisturbMode")
    aw_disturb_multi_range: list[list[int]] | None = Field(
        None, alias="awDisturbMultiRange"
    )
    clean_water_lack_light: int | None = Field(None, alias="cleanWaterLackLight")
    clean_water_empty_light: int | None = Field(None, alias="cleanWaterEmptyLight")
    waste_water_full_light: int | None = Field(None, alias="wasteWaterFullLight")
    wl_disturb_mode: int | None = Field(None, alias="wlDisturbMode")
    wl_disturb_multi_range: list[list[int]] | None = Field(
        None, alias="wlDisturbMultiRange"
    )
    control_settings: int | None = Field(None, alias="controlSettings")
    log_switch: int | None = Field(None, alias="logSwitch")


class Status(BaseModel):
    """Dataclass for status details.
    -> WaterFountainData subclass.
    """

    detect_status: int | None = Field(None, alias="detectStatus")
    electric_status: int | None = Field(None, alias="electricStatus")
    power_status: int | None = Field(None, alias="powerStatus")
    run_status: int | None = Field(None, alias="runStatus")
    suspend_status: int | None = Field(None, alias="suspendStatus")


class WaterFountainRecord(BaseModel):
    """Dataclass for feeder record data."""

    data_type: ClassVar[str] = DEVICE_RECORDS

    day_time: int | None = Field(None, alias="dayTime")
    stay_time: int | None = Field(None, alias="stayTime")
    work_time: int | None = Field(None, alias="workTime")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str | None:
        """Get the endpoint URL for the given device type."""
        if device_type == CTW3:
            return PetkitEndpoint.GET_WORK_RECORD
        return None

    @classmethod
    def query_param(
        cls,
        device: Device,
        device_data: Any | None = None,
        request_date: str | None = None,
    ) -> dict:
        """Generate query parameters including request_date."""
        if request_date is None:
            request_date = datetime.now().strftime("%Y%m%d")
        if device_data is None or not hasattr(device_data, "user_id"):
            raise ValueError("The device_data does not have a valid user_id.")
        return {
            "day": int(request_date),
            "deviceId": device.device_id,
            "userId": device_data.user_id,
        }


class FountainState(BaseModel):
    """Dataclass for device state.
    -> WaterFountain subclass (EVERSWEET ULTRA AI).
    """

    wifi: Wifi | None = None
    pim: int | None = None
    ota: int | None = None
    overall: int | None = None
    power: int | None = None
    heat_install: int | None = Field(None, alias="heatInstall")
    stg_install: int | None = Field(None, alias="stgInstall")
    cwt_install: int | None = Field(None, alias="cwtInstall")
    wt_install: int | None = Field(None, alias="wtInstall")
    heat_state: int | None = Field(None, alias="heatState")
    lift_valve_state: int | None = Field(None, alias="liftValveState")
    lift_live_state: int | None = Field(None, alias="liftLiveState")
    pump_state: int | None = Field(None, alias="pumpState")
    water_pump_state: int | None = Field(None, alias="waterPumpState")
    cwt_state: int | None = Field(None, alias="cwtState")
    wt_state: int | None = Field(None, alias="wtState")
    add_water_state: int | None = Field(None, alias="addWaterState")
    flush_state: int | None = Field(None, alias="flushState")
    drink_time: int | None = Field(None, alias="drinkTime")
    pet_time: int | None = Field(None, alias="petTime")
    pet_close_time: int | None = Field(None, alias="petCloseTime")
    lift_reset_state: int | None = Field(None, alias="liftResetState")
    stg_full_state: int | None = Field(None, alias="stgFullState")
    disinfect_time: int | None = Field(None, alias="disinfectTime")
    heat_left_time: int | None = Field(None, alias="heatLeftTime")
    heat_status_time: int | None = Field(None, alias="heatStatusTime")
    disinfect_state: int | None = Field(None, alias="disinfectState")
    filter_left_days: int | None = Field(None, alias="filterLeftDays")
    filter_updated_at: int | None = Field(None, alias="filterUpdatedAt")
    heat_real_temp: int | None = Field(None, alias="heatRealTemp")
    add_water_frequent: int | None = Field(None, alias="addWaterFrequent")
    camera_status: int | None = Field(None, alias="cameraStatus")


class WaterFountain(BaseModel):
    """Dataclass for Water Fountain Data.
    Supported devices = CTW2, CTW3, W7H
    """

    data_type: ClassVar[str] = DEVICE_DATA

    id: int
    mac: str | None = None
    sn: str
    secret: str | None = None
    created_at: str | None = Field(None, alias="createdAt")
    name: str
    hardware: int
    firmware: float | str  # str pour "412" (W4), float pour CTW3
    timezone: float | None = None
    locale: str | None = None
    settings: SettingsFountain | None = None
    device_records: list[WaterFountainRecord] | None = None
    device_nfo: Device | None = None
    # --- Ble fountains fields ---
    breakdown_warning: int | None = Field(None, alias="breakdownWarning")
    electricity: Electricity | None = None
    expected_clean_water: int | None = Field(None, alias="expectedCleanWater")
    expected_use_electricity: float | None = Field(None, alias="expectedUseElectricity")
    filter_expected_days: int | None = Field(None, alias="filterExpectedDays")
    filter_percent: int | None = Field(None, alias="filterPercent")
    filter_warning: int | None = Field(None, alias="filterWarning")
    is_night_no_disturbing: int | None = Field(None, alias="isNightNoDisturbing")
    lack_warning: int | None = Field(None, alias="lackWarning")
    low_battery: int | None = Field(None, alias="lowBattery")
    mode: int | None = None
    module_status: int | None = Field(None, alias="moduleStatus")
    record_automatic_add_water: int | None = Field(
        None, alias="recordAutomaticAddWater"
    )
    schedule: Schedule | None = None
    sync_time: str | None = Field(None, alias="syncTime")
    today_clean_water: int | None = Field(None, alias="todayCleanWater")
    today_pump_run_time: int | None = Field(None, alias="todayPumpRunTime")
    today_use_electricity: float | None = Field(None, alias="todayUseElectricity")
    update_at: str | None = Field(None, alias="updateAt")
    user_id: str | None = Field(None, alias="userId")
    water_pump_run_time: int | None = Field(None, alias="waterPumpRunTime")
    status: Status | None = None

    # --- EVERSWEET ULTRA AI fields ---
    firmware_details: list[FirmwareDetail] = Field(alias="firmwareDetails")
    signup_at: str | None = Field(None, alias="signupAt")
    share_open: int | None = Field(None, alias="shareOpen")
    auto_upgrade: int | None = Field(None, alias="autoUpgrade")
    relation: Any | None = None  # Relation existante
    model_code: int | None = Field(None, alias="modelCode")
    bt_mac: str | None = Field(None, alias="btMac")
    multi_config: bool | None = None
    state: FountainState | None = None
    cloud_product: CloudProduct | None = Field(None, alias="cloudProduct")
    live_feed: LiveFeed | None = None
    p2p_type: int | None = Field(None, alias="p2pType")
    service_status: int | None = Field(None, alias="serviceStatus")
    pet_drink_tips: list[Any] | None = Field(None, alias="petDrinkTips")
    is_pet_drink_tips: int | None = Field(None, alias="isPetDrinkTips")
    wt_tip: int | None = Field(None, alias="wtTip")
    cwt_tip: int | None = Field(None, alias="cwtTip")
    temp_range: list[int] | None = Field(None, alias="tempRange")
    too_many_pets: int | None = Field(None, alias="tooManyPets")
    frequency_pet_tip: int | None = Field(None, alias="frequencyPetTip")
    user: UserDevice | None = None
    # --- Internal tracking fields ---
    ble_connection_state: int = 2
    ble_counter: int = 0
    last_ble_poll: str | None = None

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        if device_type == W7H:
            # Wifi based fountain
            return PetkitEndpoint.DEVICE_DETAIL
        # Ble fountain
        return PetkitEndpoint.DEVICE_DATA

    @classmethod
    def query_param(
        cls,
        device: Device,
        device_data: Any | None = None,
    ) -> dict:
        """Generate query parameters including request_date."""
        return {"id": device.device_id}
