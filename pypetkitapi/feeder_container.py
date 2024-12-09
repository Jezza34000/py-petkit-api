"""Dataclasses for feeder data."""

from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import PetkitEndpoint
from pypetkitapi.containers import CloudProduct, FirmwareDetail, Wifi


class FeedItem(BaseModel):
    """Dataclass for feed item data."""

    id: str | None = None
    name: str | None = None
    time: int | None = None
    amount: int | None = None
    amount1: int | None = Field(None, alias="amount1")
    amount2: int | None = Field(None, alias="amount2")


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
    time: list[tuple[int, int]] | None = None


class SettingsFeeder(BaseModel):
    """Dataclass for settings."""

    attire_id: int | None = Field(None, alias="attireId")
    attire_switch: int | None = Field(None, alias="attireSwitch")
    auto_product: int | None = Field(None, alias="autoProduct")
    camera: int | None = None
    camera_config: int | None = Field(None, alias="cameraConfig")
    camera_multi_range: list | None = Field(None, alias="cameraMultiRange")
    control_settings: int | None = Field(None, alias="controlSettings")
    desiccant_notify: int | None = Field(None, alias="desiccantNotify")
    detect_config: int | None = Field(None, alias="detectConfig")
    detect_interval: int | None = Field(None, alias="detectInterval")
    detect_multi_range: list | None = Field(None, alias="detectMultiRange")
    eat_detection: int | None = Field(None, alias="eatDetection")
    eat_notify: int | None = Field(None, alias="eatNotify")
    eat_sensitivity: int | None = Field(None, alias="eatSensitivity")
    eat_video: int | None = Field(None, alias="eatVideo")
    feed_notify: int | None = Field(None, alias="feedNotify")
    feed_picture: int | None = Field(None, alias="feedPicture")
    food_notify: int | None = Field(None, alias="foodNotify")
    food_warn: int | None = Field(None, alias="foodWarn")
    food_warn_range: list[int] | None = Field(None, alias="foodWarnRange")
    highlight: int | None = None
    light_config: int | None = Field(None, alias="lightConfig")
    light_mode: int | None = Field(None, alias="lightMode")
    light_multi_range: list[tuple[int, int]] | None = Field(
        None, alias="lightMultiRange"
    )
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
    smart_frame: int | None = Field(None, alias="smartFrame")
    sound_enable: int | None = Field(None, alias="soundEnable")
    surplus_control: int | None = Field(None, alias="surplusControl")
    surplus_standard: int | None = Field(None, alias="surplusStandard")
    system_sound_enable: int | None = Field(None, alias="systemSoundEnable")
    time_display: int | None = Field(None, alias="timeDisplay")
    tone_config: int | None = Field(None, alias="toneConfig")
    tone_mode: int | None = Field(None, alias="toneMode")
    tone_multi_range: list[tuple[int, int]] | None = Field(None, alias="toneMultiRange")
    upload: int | None = None
    volume: int | None = None
    feed_sound: int | None = Field(None, alias="feedSound")
    factor: int | None = None
    color_setting: int | None = Field(None, alias="colorSetting")
    conservation: int | None = None
    bucket_name1: str | None = Field(None, alias="bucketName1")
    bucket_name2: str | None = Field(None, alias="bucketName2")
    camera_multi_new: list[CameraMultiNew] | None = Field(None, alias="cameraMultiNew")


class FeedState(BaseModel):
    """Dataclass for feed state data."""

    eat_avg: int | None = Field(None, alias="eatAvg")
    eat_count: int | None = Field(None, alias="eatCount")
    eat_times: list[int] | None = Field(None, alias="eatTimes")
    feed_times: dict | None = Field(None, alias="feedTimes")
    times: int | None = None
    add_amount_total: int | None = Field(None, alias="addAmountTotal")
    plan_amount_total: int | None = Field(None, alias="planAmountTotal")
    plan_real_amount_total: int | None = Field(None, alias="planRealAmountTotal")
    real_amount_total: int | None = Field(None, alias="realAmountTotal")
    add_amount_total1: int | None = Field(None, alias="addAmountTotal1")
    add_amount_total2: int | None = Field(None, alias="addAmountTotal2")
    plan_amount_total1: int | None = Field(None, alias="planAmountTotal1")
    plan_amount_total2: int | None = Field(None, alias="planAmountTotal2")
    plan_real_amount_total1: int | None = Field(None, alias="planRealAmountTotal1")
    plan_real_amount_total2: int | None = Field(None, alias="planRealAmountTotal2")
    real_amount_total1: int | None = Field(None, alias="realAmountTotal1")
    real_amount_total2: int | None = Field(None, alias="realAmountTotal2")


class StateFeeder(BaseModel):
    """Dataclass for state data."""

    battery_power: int | None = Field(None, alias="batteryPower")
    battery_status: int | None = Field(None, alias="batteryStatus")
    bowl: int | None = None
    camera_status: int | None = Field(None, alias="cameraStatus")
    desiccant_left_days: int | None = Field(None, alias="desiccantLeftDays")
    desiccant_time: int | None = Field(None, alias="desiccantTime")
    door: int | None = None
    feed_state: FeedState | None = Field(None, alias="feedState")
    feeding: int | None = None
    ota: int | None = None
    overall: int | None = None
    pim: int | None = None
    runtime: int | None = None
    wifi: Wifi | None = None
    eating: int | None = None
    food: int | None = None
    food1: int | None = Field(None, alias="food1")
    food2: int | None = Field(None, alias="food2")
    conservation_status: int | None = Field(None, alias="conservationStatus")


class Feeder(BaseModel):
    """Dataclass for feeder data."""

    url_endpoint: ClassVar[PetkitEndpoint] = PetkitEndpoint.DEVICE_DETAIL
    query_param: ClassVar[Callable] = lambda device_id: {"id": device_id}

    auto_upgrade: int | None = Field(None, alias="autoUpgrade")
    bt_mac: str | None = Field(None, alias="btMac")
    cloud_product: CloudProduct | None = Field(None, alias="cloudProduct")
    created_at: str | None = Field(None, alias="createdAt")
    firmware: str | None = None
    firmware_details: list[FirmwareDetail] | None = Field(None, alias="firmwareDetails")
    hardware: int | None = None
    id: int | None = None
    locale: str | None = None
    mac: str | None = None
    model_code: int | None = Field(None, alias="modelCode")
    multi_feed_item: MultiFeedItem | None = Field(None, alias="multiFeedItem")
    name: str | None = None
    secret: str | None = None
    service_status: int | None = Field(None, alias="serviceStatus")
    settings: SettingsFeeder | None = None
    share_open: int | None = Field(None, alias="shareOpen")
    signup_at: str | None = Field(None, alias="signupAt")
    sn: str | None = None
    state: StateFeeder | None = None
    timezone: float | None = None
    p2p_type: int | None = Field(None, alias="p2pType")
    multi_config: bool | None = Field(None, alias="multiConfig")
    device_type: str | None = Field(None, alias="deviceType")
    manual_feed_id: int = 0

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return cls.url_endpoint.value


class EventState(BaseModel):
    """Dataclass for event state data."""

    completed_at: str | None = Field(None, alias="completedAt")
    err_code: int | None = Field(None, alias="errCode")
    media: int | None = None
    real_amount1: int | None = Field(None, alias="realAmount1")
    real_amount2: int | None = Field(None, alias="realAmount2")
    result: int | None = None
    surplus_standard: int | None = Field(None, alias="surplusStandard")


class FeederRecord(BaseModel):
    """Dataclass for feeder record data."""

    aes_key: str | None = Field(None, alias="aesKey")
    duration: int | None = None
    event_id: str | None = Field(None, alias="eventId")
    expire: int | None = None
    mark: int | None = None
    media_api: str | None = Field(None, alias="mediaApi")
    start_time: int | None = Field(None, alias="startTime")
    storage_space: int | None = Field(None, alias="storageSpace")
    eat_video: int | None = Field(None, alias="eatVideo")
    is_need_upload_video: int | None = Field(None, alias="isNeedUploadVideo")
    preview: str | None = None
    time: int | None = None
    timestamp: int | None = None
    aes_key1: str | None = Field(None, alias="aesKey1")
    aes_key2: str | None = Field(None, alias="aesKey2")
    amount1: int | None = Field(None, alias="amount1")
    amount2: int | None = Field(None, alias="amount2")
    completed_at: int | None = Field(None, alias="completedAt")
    content: dict[str, Any] | None = None
    desc: str | None = None
    device_id: int | None = Field(None, alias="deviceId")
    eat_end_time: int | None = Field(None, alias="eatEndTime")
    eat_start_time: int | None = Field(None, alias="eatStartTime")
    empty: int | None = None
    end_time: int | None = Field(None, alias="endTime")
    enum_event_type: str | None = Field(None, alias="enumEventType")
    event: str | None = None
    event_type: int | None = Field(None, alias="eventType")
    expire1: int | None = Field(None, alias="expire1")
    expire2: int | None = Field(None, alias="expire2")
    id: str | None = None
    is_executed: int | None = Field(None, alias="isExecuted")
    media_list: list[Any] | None = Field(None, alias="mediaList")
    name: str | None = None
    preview1: str | None = Field(None, alias="preview1")
    preview2: str | None = Field(None, alias="preview2")
    src: int | None = None
    state: EventState | None = None
    status: int | None = None
