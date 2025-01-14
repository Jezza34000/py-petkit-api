"""Dataclasses for feeder data."""

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import (
    D3,
    D4,
    D4S,
    DEVICE_DATA,
    DEVICE_RECORDS,
    FEEDER_MINI,
    PetkitEndpoint,
)
from pypetkitapi.containers import (
    CloudProduct,
    Device,
    FirmwareDetail,
    UserDevice,
    Wifi,
)


class FeedItem(BaseModel):
    """Dataclass for feed item data."""

    amount: int | None = None
    amount1: int | None = Field(None, alias="amount1")
    amount2: int | None = Field(None, alias="amount2")
    id: str | None = None
    name: str | None = None
    time: int | None = None


class FeedDailyList(BaseModel):
    """Dataclass for feed daily list data."""

    items: list[FeedItem] | None = None
    repeats: int | None = None
    suspended: int | None = None


class MultiFeedItem(BaseModel):
    """Dataclass for multi feed item data."""

    feed_daily_list: list[FeedDailyList] | None = Field(None, alias="feedDailyList")
    is_executed: int | None = Field(None, alias="isExecuted")
    user_id: str | None = Field(None, alias="userId")


class CameraMultiNew(BaseModel):
    """Dataclass for camera multi new data."""

    enable: int | None = None
    rpt: str | None = None
    time: list[list[int]] | None = None


class SettingsFeeder(BaseModel):
    """Dataclass for settings."""

    attire_id: int | None = Field(None, alias="attireId")
    attire_switch: int | None = Field(None, alias="attireSwitch")
    auto_product: int | None = Field(None, alias="autoProduct")
    bucket_name1: str | None = Field(None, alias="bucketName1")
    bucket_name2: str | None = Field(None, alias="bucketName2")
    camera: int | None = None
    camera_config: int | None = Field(None, alias="cameraConfig")
    camera_multi_new: list[CameraMultiNew] | None = Field(None, alias="cameraMultiNew")
    camera_multi_range: list | None = Field(None, alias="cameraMultiRange")
    color_setting: int | None = None
    conservation: int | None = None
    control_settings: int | None = Field(None, alias="controlSettings")
    desiccant_notify: int | None = Field(None, alias="desiccantNotify")
    detect_config: int | None = Field(None, alias="detectConfig")
    detect_interval: int | None = Field(None, alias="detectInterval")
    detect_multi_range: list | None = Field(None, alias="detectMultiRange")
    eat_detection: int | None = Field(None, alias="eatDetection")
    eat_notify: int | None = Field(None, alias="eatNotify")
    eat_sensitivity: int | None = Field(None, alias="eatSensitivity")
    eat_video: int | None = Field(None, alias="eatVideo")
    factor: int | None = None
    feed_notify: int | None = Field(None, alias="feedNotify")
    feed_picture: int | None = Field(None, alias="feedPicture")
    feed_sound: int | None = Field(None, alias="feedSound")
    food_notify: int | None = Field(None, alias="foodNotify")
    food_warn: int | None = Field(None, alias="foodWarn")
    food_warn_range: list[int] | None = Field(None, alias="foodWarnRange")
    highlight: int | None = None
    light_config: int | None = Field(None, alias="lightConfig")
    light_mode: int | None = Field(None, alias="lightMode")
    light_multi_range: list[list[int]] | None = Field(None, alias="lightMultiRange")
    live_encrypt: int | None = Field(None, alias="liveEncrypt")
    low_battery_notify: int | None = Field(None, alias="lowBatteryNotify")
    manual_lock: int | None = Field(None, alias="manualLock")
    microphone: int | None = None
    move_detection: int | None = Field(None, alias="moveDetection")
    move_notify: int | None = Field(None, alias="moveNotify")
    move_sensitivity: int | None = Field(None, alias="moveSensitivity")
    night: int | None = None
    num_limit: int | None = Field(None, alias="numLimit")
    pet_detection: int | None = Field(None, alias="petDetection")
    pet_notify: int | None = Field(None, alias="petNotify")
    pet_sensitivity: int | None = Field(None, alias="petSensitivity")
    pre_live: int | None = Field(None, alias="preLive")
    selected_sound: int | None = Field(None, alias="selectedSound")
    shortest: int | None = None  # D4S
    smart_frame: int | None = Field(None, alias="smartFrame")
    sound_enable: int | None = Field(None, alias="soundEnable")
    surplus: int | None = None  # D3
    surplus_control: int | None = Field(None, alias="surplusControl")
    surplus_standard: int | None = Field(None, alias="surplusStandard")
    system_sound_enable: int | None = Field(None, alias="systemSoundEnable")
    time_display: int | None = Field(None, alias="timeDisplay")
    tone_config: int | None = Field(None, alias="toneConfig")
    tone_mode: int | None = Field(None, alias="toneMode")
    tone_multi_range: list[list[int]] | None = Field(None, alias="toneMultiRange")
    upload: int | None = None
    volume: int | None = None


class FeedState(BaseModel):
    """Dataclass for feed state data."""

    add_amount_total: int | None = Field(None, alias="addAmountTotal")
    add_amount_total1: int | None = Field(None, alias="addAmountTotal1")
    add_amount_total2: int | None = Field(None, alias="addAmountTotal2")
    eat_amount_total: int | None = Field(None, alias="eatAmountTotal")  # D3
    eat_avg: int | None = Field(None, alias="eatAvg")
    eat_count: int | None = Field(None, alias="eatCount")
    eat_times: list[int] | None = Field(None, alias="eatTimes")
    feed_times: dict | list | None = Field(None, alias="feedTimes")
    plan_amount_total: int | None = Field(None, alias="planAmountTotal")
    plan_amount_total1: int | None = Field(None, alias="planAmountTotal1")
    plan_amount_total2: int | None = Field(None, alias="planAmountTotal2")
    plan_real_amount_total: int | None = Field(None, alias="planRealAmountTotal")
    plan_real_amount_total1: int | None = Field(None, alias="planRealAmountTotal1")
    plan_real_amount_total2: int | None = Field(None, alias="planRealAmountTotal2")
    real_amount_total: int | None = Field(None, alias="realAmountTotal")
    real_amount_total1: int | None = Field(None, alias="realAmountTotal1")
    real_amount_total2: int | None = Field(None, alias="realAmountTotal2")
    times: int | None = None


class StateFeeder(BaseModel):
    """Dataclass for state data."""

    battery_power: int | None = Field(None, alias="batteryPower")
    battery_status: int | None = Field(None, alias="batteryStatus")
    block: int | None = None
    bowl: int | None = None
    broadcast: dict | None = None
    camera_status: int | None = Field(None, alias="cameraStatus")
    charge: int | None = None
    conservation_status: int | None = Field(None, alias="conservationStatus")
    desiccant_left_days: int | None = Field(None, alias="desiccantLeftDays")
    desiccant_time: int | None = Field(None, alias="desiccantTime")
    door: int | None = None
    eating: int | None = None
    error_code: str | None = Field(None, alias="errorCode")
    error_detail: str | None = Field(None, alias="errorDetail")
    error_level: int | None = Field(None, alias="errorLevel")
    error_msg: str | None = Field(None, alias="errorMsg")
    feed_state: FeedState | None = Field(None, alias="feedState")
    feeding: int | None = None
    food: int | None = None
    food1: int | None = Field(None, alias="food1")
    food2: int | None = Field(None, alias="food2")
    ota: int | None = None
    overall: int | None = None
    pim: int | None = None
    runtime: int | None = None
    weight: int | None = None
    wifi: Wifi | None = None


class ManualFeed(BaseModel):
    """Dataclass for result data."""

    amount: int | None = None
    amount1: int | None = None
    amount2: int | None = None
    id: str | None = None
    is_executed: int | None = Field(None, alias="isExecuted")
    is_need_upload_video: int | None = Field(None, alias="isNeedUploadVideo")
    src: int | None = None
    status: int | None = None
    time: int | None = None


class EventState(BaseModel):
    """Dataclass for event state data."""

    completed_at: str | None = Field(None, alias="completedAt")
    err_code: int | None = Field(None, alias="errCode")
    media: int | None = None
    real_amount: int | None = Field(None, alias="realAmount")
    real_amount1: int | None = Field(None, alias="realAmount1")
    real_amount2: int | None = Field(None, alias="realAmount2")
    result: int | None = None
    surplus_standard: int | None = Field(None, alias="surplusStandard")


class RecordsItems(BaseModel):
    """Dataclass for records items data."""

    aes_key: str | None = Field(None, alias="aesKey")
    aes_key1: str | None = Field(None, alias="aesKey1")
    aes_key2: str | None = Field(None, alias="aesKey2")
    amount: int | None = Field(None, alias="amount")
    amount1: int | None = Field(None, alias="amount1")
    amount2: int | None = Field(None, alias="amount2")
    completed_at: int | None = Field(None, alias="completedAt")
    content: dict[str, Any] | None = None
    desc: str | None = None
    device_id: int | None = Field(None, alias="deviceId")
    duration: int | None = None
    eat_end_time: int | None = Field(None, alias="eatEndTime")
    eat_start_time: int | None = Field(None, alias="eatStartTime")
    eat_video: int | None = Field(None, alias="eatVideo")
    eat_weight: int | None = Field(None, alias="eatWeight")  # D3
    empty: int | None = None
    end_time: int | None = Field(None, alias="endTime")
    enum_event_type: str | None = Field(None, alias="enumEventType")
    event: str | None = None
    event_id: str | None = Field(None, alias="eventId")
    event_type: int | None = Field(None, alias="eventType")
    expire: int | None = None
    expire1: int | None = Field(None, alias="expire1")
    expire2: int | None = Field(None, alias="expire2")
    id: str | None = None
    is_executed: int | None = Field(None, alias="isExecuted")
    is_need_upload_video: int | None = Field(None, alias="isNeedUploadVideo")
    left_weight: int | None = Field(None, alias="leftWeight")  # D3
    mark: int | None = None
    media_api: str | None = Field(None, alias="mediaApi")
    media_list: list[Any] | None = Field(None, alias="mediaList")
    name: str | None = None
    pet_id: str | None = Field(None, alias="petId")
    preview: str | None = None
    preview1: str | None = Field(None, alias="preview1")
    preview2: str | None = Field(None, alias="preview2")
    src: int | None = None
    start_time: int | None = Field(None, alias="startTime")
    state: EventState | None = None
    status: int | None = None
    storage_space: int | None = Field(None, alias="storageSpace")
    time: int | None = None
    timestamp: int | None = None


class RecordsType(BaseModel):
    """Dataclass for records type data."""

    add_amount: int | None = Field(None, alias="addAmount")
    add_amount1: int | None = Field(None, alias="addAmount1")
    add_amount2: int | None = Field(None, alias="addAmount2")
    day: int | None = None
    device_id: int | None = Field(None, alias="deviceId")
    eat_count: int | None = Field(None, alias="eatCount")
    eat_amount: int | None = Field(None, alias="eatAmount")  # D3
    items: list[RecordsItems] | None = None
    plan_amount: int | None = Field(None, alias="planAmount")
    real_amount: int | None = Field(None, alias="realAmount")
    amount: int | None = None
    times: int | None = None
    user_id: str | None = Field(None, alias="userId")  # D3


class FeederRecord(BaseModel):
    """Dataclass for feeder record data."""

    data_type: ClassVar[str] = DEVICE_RECORDS

    eat: list[RecordsType] | None = None
    feed: list[RecordsType] | None = None
    move: list[RecordsType] | None = None
    pet: list[RecordsType] | None = None
    device_type: str | None = Field(None, alias="deviceType")
    type_code: int = Field(0, alias="typeCode")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str | None:
        """Get the endpoint URL for the given device type."""
        if device_type == D3:
            return PetkitEndpoint.DAILY_FEED_AND_EAT
        if device_type == D4:
            return PetkitEndpoint.FEED_STATISTIC
        if device_type in D4S:
            return PetkitEndpoint.DAILY_FEED
        if device_type in FEEDER_MINI:
            return PetkitEndpoint.DAILY_FEED.lower()  # Workaround for Feeder Mini
        return PetkitEndpoint.GET_DEVICE_RECORD

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

        if device.device_type == D4:
            return {"date": request_date, "type": 0, "deviceId": device.device_id}
        return {"days": request_date, "deviceId": device.device_id}


class Feeder(BaseModel):
    """Dataclass for feeder data."""

    data_type: ClassVar[str] = DEVICE_DATA

    auto_upgrade: int | None = Field(None, alias="autoUpgrade")
    bt_mac: str | None = Field(None, alias="btMac")
    cloud_product: CloudProduct | None = Field(None, alias="cloudProduct")
    created_at: str | None = Field(None, alias="createdAt")
    desc: str | None = None  # D3
    device_records: FeederRecord | None = None
    firmware: str
    firmware_details: list[FirmwareDetail] | None = Field(None, alias="firmwareDetails")
    hardware: int
    id: int
    locale: str | None = None
    mac: str | None = None
    manual_feed: ManualFeed | None = None
    model_code: int | None = Field(None, alias="modelCode")
    multi_config: bool | None = Field(None, alias="multiConfig")
    multi_feed_item: MultiFeedItem | None = Field(None, alias="multiFeedItem")
    name: str | None = None
    p2p_type: int | None = Field(None, alias="p2pType")
    secret: str | None = None
    service_status: int | None = Field(None, alias="serviceStatus")
    settings: SettingsFeeder | None = None
    share_open: int | None = Field(None, alias="shareOpen")
    signup_at: str | None = Field(None, alias="signupAt")
    sn: str
    state: StateFeeder | None = None
    timezone: float | None = None
    user: UserDevice | None = None
    device_nfo: Device | None = None
    medias: list | None = None

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return PetkitEndpoint.DEVICE_DETAIL

    @classmethod
    def query_param(
        cls,
        device: Device,
        device_data: Any | None = None,
    ) -> dict:
        """Generate query parameters including request_date."""
        return {"id": int(device.device_id)}
