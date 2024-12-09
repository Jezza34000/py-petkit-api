"""Dataclasses for Litter."""

from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import PetkitEndpoint
from pypetkitapi.containers import CloudProduct, FirmwareDetail, Wifi


class SettingsLitter(BaseModel):
    """Dataclass for settings.
    -> LitterData subclass.
    """

    auto_interval_min: int | None = Field(None, alias="autoIntervalMin")
    auto_work: int | None = Field(None, alias="autoWork")
    avoid_repeat: int | None = Field(None, alias="avoidRepeat")
    bury: int | None = None
    control_settings: int | None = Field(None, alias="controlSettings")
    deep_clean: int | None = Field(None, alias="deepClean")
    deep_refresh: int | None = Field(None, alias="deepRefresh")
    deodorant_notify: int | None = Field(None, alias="deodorantNotify")
    distrub_multi_range: list[list[int]] | None = Field(None, alias="distrubMultiRange")
    disturb_config: int | None = Field(None, alias="disturbConfig")
    disturb_mode: int | None = Field(None, alias="disturbMode")
    disturb_range: list[int] | None = Field(None, alias="disturbRange")
    downpos: int | None = None
    dump_switch: int | None = Field(None, alias="dumpSwitch")
    fixed_time_clear: int | None = Field(None, alias="fixedTimeClear")
    kitten: int | None = None
    kitten_percent: float | None = Field(None, alias="kittenPercent")
    kitten_tips_time: int | None = Field(None, alias="kittenTipsTime")
    lack_liquid_notify: int | None = Field(None, alias="lackLiquidNotify")
    lack_sand_notify: int | None = Field(None, alias="lackSandNotify")
    language: str | None = None
    language_follow: int | None = Field(None, alias="languageFollow")
    languages: list[str] | None = None
    light_config: int | None = Field(None, alias="lightConfig")
    light_mode: int | None = Field(None, alias="lightMode")
    light_multi_range: list[Any] | None = Field(None, alias="lightMultiRange")
    light_range: list[int] | None = Field(None, alias="lightRange")
    lightest: int | None = Field(None, alias="lightest")
    litter_full_notify: int | None = Field(None, alias="litterFullNotify")
    manual_lock: int | None = Field(None, alias="manualLock")
    pet_in_notify: int | None = Field(None, alias="petInNotify")
    relate_k3_switch: int | None = Field(None, alias="relateK3Switch")
    sand_type: int | None = Field(None, alias="sandType")
    soft_mode: int | None = Field(None, alias="softMode")
    still_time: int | None = Field(None, alias="stillTime")
    stop_time: int | None = Field(None, alias="stopTime")
    underweight: int | None = Field(None, alias="underweight")
    unit: int | None = None
    weight_popup: int | None = Field(None, alias="weightPopup")
    work_notify: int | None = Field(None, alias="workNotify")
    auto_product: int | None = Field(None, alias="autoProduct")
    camera: int | None = None
    camera_config: int | None = Field(None, alias="cameraConfig")
    cleanning_notify: int | None = Field(None, alias="cleanningNotify")
    garbage_notify: int | None = Field(None, alias="garbageNotify")
    highlight: int | None = Field(None, alias="highlight")
    light_assist: int | None = Field(None, alias="lightAssist")
    live_encrypt: int | None = Field(None, alias="liveEncrypt")
    microphone: int | None = None
    move_notify: int | None = Field(None, alias="moveNotify")
    night: int | None = None
    package_standard: list[int] | None = Field(None, alias="packageStandard")
    pet_detection: int | None = Field(None, alias="petDetection")
    pet_notify: int | None = Field(None, alias="petNotify")
    pre_live: int | None = Field(None, alias="preLive")
    system_sound_enable: int | None = Field(None, alias="systemSoundEnable")
    time_display: int | None = Field(None, alias="timeDisplay")
    toilet_detection: int | None = Field(None, alias="toiletDetection")
    toilet_notify: int | None = Field(None, alias="toiletNotify")
    tone_config: int | None = Field(None, alias="toneConfig")
    tone_mode: int | None = Field(None, alias="toneMode")
    tone_multi_range: list[list[int]] | None = Field(None, alias="toneMultiRange")
    tumbling: int | None = None
    upload: int | None = None
    volume: int | None = None
    wander_detection: int | None = Field(None, alias="wanderDetection")


class StateLitter(BaseModel):
    """Dataclass for state.
    -> LitterData subclass.
    """

    box: int | None = None
    box_full: bool | None = Field(None, alias="boxFull")
    box_state: int | None = Field(None, alias="boxState")
    deodorant_left_days: int | None = Field(None, alias="deodorantLeftDays")
    frequent_restroom: int | None = Field(None, alias="frequentRestroom")
    liquid_empty: bool | None = Field(None, alias="liquidEmpty")
    liquid_lack: bool | None = Field(None, alias="liquidLack")
    liquid_reset: int | None = Field(None, alias="liquidReset")
    low_power: bool | None = Field(None, alias="lowPower")
    offline_time: int | None = Field(None, alias="offlineTime")
    ota: int | None = None
    overall: int | None = None
    pet_error: bool | None = Field(None, alias="petError")
    pet_in_time: int | None = Field(None, alias="petInTime")
    pim: int | None = None
    power: int | None = None
    sand_correct: int | None = Field(None, alias="sandCorrect")
    sand_lack: bool | None = Field(None, alias="sandLack")
    sand_percent: int | None = Field(None, alias="sandPercent")
    sand_status: int | None = Field(None, alias="sandStatus")
    sand_type: int | None = Field(None, alias="sandType")
    sand_weight: int | None = Field(None, alias="sandWeight")
    used_times: int | None = Field(None, alias="usedTimes")
    wifi: Wifi | None = None
    bagging_state: int | None = Field(None, alias="baggingState")
    battery: int | None = None
    box_store_state: int | None = Field(None, alias="boxStoreState")
    camera_status: int | None = Field(None, alias="cameraStatus")
    dump_state: int | None = Field(None, alias="dumpState")
    liquid: int | None = None
    pack_state: int | None = Field(None, alias="packState")
    package_install: int | None = Field(None, alias="packageInstall")
    package_secret: str | None = Field(None, alias="packageSecret")
    package_sn: str | None = Field(None, alias="packageSn")
    package_state: int | None = Field(None, alias="packageState")
    pi_ins: int | None = Field(None, alias="piIns")
    purification_left_days: int | None = Field(None, alias="purificationLeftDays")
    seal_door_state: int | None = Field(None, alias="sealDoorState")
    top_ins: int | None = Field(None, alias="topIns")
    wander_time: int | None = Field(None, alias="wanderTime")


class Litter(BaseModel):
    """Dataclass for Litter Data.
    Supported devices = T4, T6
    """

    url_endpoint: ClassVar[PetkitEndpoint] = PetkitEndpoint.DEVICE_DETAIL
    query_param: ClassVar[Callable] = lambda device_id: {"id": device_id}

    auto_upgrade: int | None = Field(None, alias="autoUpgrade")
    bt_mac: str | None = Field(None, alias="btMac")
    created_at: str | None = Field(None, alias="createdAt")
    firmware: str | None = None
    firmware_details: list[FirmwareDetail] | None = Field(None, alias="firmwareDetails")
    hardware: int | None = None
    id: int | None = None
    is_pet_out_tips: int | None = Field(None, alias="isPetOutTips")
    locale: str | None = None
    mac: str | None = None
    maintenance_time: int | None = Field(None, alias="maintenanceTime")
    multi_config: bool | None = Field(None, alias="multiConfig")
    name: str | None = None
    pet_in_tip_limit: int | None = Field(None, alias="petInTipLimit")
    pet_out_tips: list[Any] | None = Field(None, alias="petOutTips")
    secret: str | None = None
    settings: SettingsLitter | None = None
    share_open: int | None = Field(None, alias="shareOpen")
    signup_at: str | None = Field(None, alias="signupAt")
    sn: str | None = None
    state: StateLitter | None = None
    timezone: float | None = None
    cloud_product: CloudProduct | None = Field(None, alias="cloudProduct")  # For T5/T6
    in_times: int | None = Field(None, alias="inTimes")
    last_out_time: int | None = Field(None, alias="lastOutTime")
    p2p_type: int | None = Field(None, alias="p2pType")
    package_ignore_state: int | None = Field(None, alias="packageIgnoreState")
    package_total_count: int | None = Field(None, alias="packageTotalCount")
    package_used_count: int | None = Field(None, alias="packageUsedCount")
    pet_out_records: list[list[int]] | None = Field(None, alias="petOutRecords")
    service_status: int | None = Field(None, alias="serviceStatus")
    total_time: int | None = Field(None, alias="totalTime")
    device_type: str | None = Field(None, alias="deviceType")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return cls.url_endpoint.value
