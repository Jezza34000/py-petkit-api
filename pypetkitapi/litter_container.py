"""Dataclasses for Litter."""

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import DEVICE_DATA, DEVICE_RECORDS, PetkitEndpoint
from pypetkitapi.containers import AccountData, CloudProduct, FirmwareDetail, Wifi


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


class WorkState(BaseModel):
    """Dataclass for work state data."""

    safe_warn: int | None = Field(None, alias="safeWarn")
    stop_time: int | None = Field(None, alias="stopTime")
    work_mode: int | None = Field(None, alias="workMode")
    work_process: int | None = Field(None, alias="workProcess")
    work_reason: int | None = Field(None, alias="workReason")
    pet_in_time: int | None = Field(None, alias="petInTime")


class StateLitter(BaseModel):
    """Dataclass for state.
    -> LitterData subclass.
    """

    box: int | None = None
    box_full: bool | None = Field(None, alias="boxFull")
    box_state: int | None = Field(None, alias="boxState")
    deodorant_left_days: int | None = Field(None, alias="deodorantLeftDays")
    error_msg: str | None = Field(None, alias="errorMsg")
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
    work_state: WorkState | None = Field(None, alias="workState")


class ContentSC(BaseModel):
    """Dataclass for content data."""

    box: int | None = None
    box_full: bool | None = Field(None, alias="boxFull")
    err: str | None = None
    litter_percent: int | None = Field(None, alias="litterPercent")
    mark: int | None = None
    media: int | None = None
    result: int | None = None
    start_reason: int | None = Field(None, alias="startReason")
    start_time: int | None = Field(None, alias="startTime")
    upload: int | None = None


class LRContent(BaseModel):
    """Dataclass for pet data."""

    auto_clear: int | None = Field(None, alias="autoClear")
    interval: int | None = None
    pet_weight: int | None = Field(None, alias="petWeight")
    time_in: int | None = Field(None, alias="timeIn")
    time_out: int | None = Field(None, alias="timeOut")
    error: int | None = None


class LRSubContent(BaseModel):
    """Dataclass for sub-content data."""

    aes_key: str | None = Field(None, alias="aesKey")
    content: ContentSC | None = None
    device_id: int | None = Field(None, alias="deviceId")
    duration: int | None = None
    enum_event_type: str | None = Field(None, alias="enumEventType")
    event_id: str | None = Field(None, alias="eventId")
    event_type: int | None = Field(None, alias="eventType")
    expire: int | None = None
    mark: int | None = None
    media: int | None = None
    media_api: str | None = Field(None, alias="mediaApi")
    preview: str | None = None
    related_event: str | None = Field(None, alias="relatedEvent")
    shit_aes_key: str | None = Field(None, alias="shitAesKey")
    shit_picture: str | None = Field(None, alias="shitPicture")
    storage_space: int | None = Field(None, alias="storageSpace")
    sub_content: list[Any] | None = Field(None, alias="subContent")
    timestamp: int | None = None
    upload: int | None = None
    user_id: str | None = Field(None, alias="userId")


class LitterRecord(BaseModel):
    """Dataclass for feeder record data."""

    data_type: ClassVar[str] = DEVICE_RECORDS

    aes_key: str | None = Field(None, alias="aesKey")
    avatar: str | None = None
    content: LRContent | None = None
    device_id: int | None = Field(None, alias="deviceId")
    duration: int | None = None
    enum_event_type: str | None = Field(None, alias="enumEventType")
    event_id: str | None = Field(None, alias="eventId")
    event_type: int | None = Field(None, alias="eventType")
    expire: int | None = None
    is_need_upload_video: int | None = Field(None, alias="isNeedUploadVideo")
    mark: int | None = None
    media: int | None = None
    media_api: str | None = Field(None, alias="mediaApi")
    pet_id: str | None = Field(None, alias="petId")
    pet_name: str | None = Field(None, alias="petName")
    preview: str | None = None
    related_event: str | None = Field(None, alias="relatedEvent")
    storage_space: int | None = Field(None, alias="storageSpace")
    sub_content: list[LRSubContent] | None = Field(None, alias="subContent")
    timestamp: int | None = None
    toilet_detection: int | None = Field(None, alias="toiletDetection")
    upload: int | None = None
    user_id: str | None = Field(None, alias="userId")
    device_type: str | None = Field(None, alias="deviceType")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return PetkitEndpoint.GET_DEVICE_RECORD

    @classmethod
    def query_param(
        cls, account: AccountData, device_id: int, request_date: str | None = None
    ) -> dict:
        """Generate query parameters including request_date."""
        if request_date is None:
            request_date = datetime.now().strftime("%Y%m%d")
        return {"date": int(request_date), "deviceId": device_id}


class Litter(BaseModel):
    """Dataclass for Litter Data.
    Supported devices = T4, T6
    """

    data_type: ClassVar[str] = DEVICE_DATA

    auto_upgrade: int | None = Field(None, alias="autoUpgrade")
    bt_mac: str | None = Field(None, alias="btMac")
    created_at: str | None = Field(None, alias="createdAt")
    firmware: float
    firmware_details: list[FirmwareDetail] = Field(alias="firmwareDetails")
    hardware: int
    id: int
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
    sn: str
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
    device_records: list[LitterRecord] | None = None

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return PetkitEndpoint.DEVICE_DETAIL

    @classmethod
    def query_param(cls, account: AccountData, device_id: int) -> dict:
        """Generate query parameters including request_date."""
        return {"id": device_id}
