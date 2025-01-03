"""Constants for the pypetkitapi library."""

from enum import StrEnum

RES_KEY = "result"
ERR_KEY = "error"
SUCCESS_KEY = "success"

DEVICE_RECORDS = "deviceRecords"
DEVICE_DATA = "deviceData"
DEVICE_STATS = "deviceStats"
PET_DATA = "petData"

# PetKit Models
FEEDER = "feeder"
FEEDER_MINI = "feedermini"
D3 = "d3"
D4 = "d4"
D4S = "d4s"
D4H = "d4h"
D4SH = "d4sh"
T3 = "t3"
T4 = "t4"
T5 = "t5"
T6 = "t6"
W5 = "w5"
CTW3 = "ctw3"
K2 = "k2"
K3 = "k3"
PET = "pet"

DEVICES_LITTER_BOX = [T3, T4, T5, T6]
DEVICES_FEEDER = [FEEDER, FEEDER_MINI, D3, D4, D4S, D4H, D4SH]
DEVICES_WATER_FOUNTAIN = [W5, CTW3]
DEVICES_PURIFIER = [K2]
ALL_DEVICES = [
    *DEVICES_LITTER_BOX,
    *DEVICES_FEEDER,
    *DEVICES_WATER_FOUNTAIN,
    *DEVICES_PURIFIER,
]


class PetkitDomain(StrEnum):
    """Petkit URL constants"""

    PASSPORT_PETKIT = "https://passport.petkt.com/"
    CHINA_SRV = "https://api.petkit.cn/6/"


class Client(StrEnum):
    """Platform constants"""

    PLATFORM_TYPE = "android"
    OS_VERSION = "15.1"
    MODEL_NAME = "23127PN0CG"
    SOURCE = "app.petkit-android"


class Header(StrEnum):
    """Header constants"""

    ACCEPT = "*/*"
    ACCEPT_LANG = "en-US;q=1, it-US;q=0.9"
    ENCODING = "gzip, deflate"
    API_VERSION = "11.3.1"
    CONTENT_TYPE = "application/x-www-form-urlencoded"
    AGENT = "okhttp/3.12.11"
    CLIENT = f"{Client.PLATFORM_TYPE}({Client.OS_VERSION};{Client.MODEL_NAME})"
    TIMEZONE = "1.0"
    TIMEZONE_ID = "Europe/Paris"  # TODO: Make this dynamic
    LOCALE = "en-US"
    IMG_VERSION = "1.0"
    HOUR = "24"


CLIENT_NFO = {
    "locale": Header.LOCALE.value,
    "name": Client.MODEL_NAME.value,
    "osVersion": Client.OS_VERSION.value,
    "platform": Client.PLATFORM_TYPE.value,
    "source": Client.SOURCE.value,
    "timezone": Header.TIMEZONE.value,  # TODO: Make this dynamic
    "timezoneId": Header.TIMEZONE_ID.value,
    "version": Header.API_VERSION.value,
}

LOGIN_DATA = {
    "client": str(CLIENT_NFO),
    "oldVersion": Header.API_VERSION,
}


class RecordType(StrEnum):
    """Record Type constants"""

    EAT = "eat"
    FEED = "feed"
    MOVE = "move"
    PET = "pet"


RecordTypeLST = [RecordType.EAT, RecordType.FEED, RecordType.MOVE, RecordType.PET]


class PetkitEndpoint(StrEnum):
    """Petkit Endpoint constants"""

    REGION_SERVERS = "v1/regionservers"
    LOGIN = "user/login"
    GET_LOGIN_CODE = "user/sendcodeforquicklogin"
    REFRESH_SESSION = "user/refreshsession"
    FAMILY_LIST = "group/family/list"
    REFRESH_HOME_V2 = "refreshHomeV2"

    # Common to many device
    DEVICE_DETAIL = "device_detail"
    DEVICE_DATA = "deviceData"
    GET_DEVICE_RECORD = "getDeviceRecord"
    GET_DEVICE_RECORD_RELEASE = "getDeviceRecordRelease"
    UPDATE_SETTING = "updateSettings"

    # Bluetooth relay
    BLE_AS_RELAY = "ble/ownSupportBleDevices"
    BLE_CONNECT = "ble/connect"
    BLE_POLL = "ble/poll"
    BLE_CANCEL = "ble/cancel"

    # Fountain & Litter Box
    CONTROL_DEVICE = "controlDevice"
    GET_WORK_RECORD = "getWorkRecord"

    # Litter Box
    DEODORANT_RESET = "deodorantReset"
    STATISTIC = "statistic"
    STATISTIC_RELEASE = "statisticRelease"
    GET_PET_OUT_GRAPH = "getPetOutGraph"

    # Video features
    CLOUD_VIDEO = "cloud/video"
    GET_DOWNLOAD_M3U8 = "getDownloadM3u8"
    GET_M3U8 = "getM3u8"

    # Feeders
    REPLENISHED_FOOD = "added"
    FRESH_ELEMENT_CALIBRATION = "food_reset"
    FRESH_ELEMENT_CANCEL_FEED = "cancel_realtime_feed"
    DESICCANT_RESET = "desiccantReset"
    MINI_DESICCANT_RESET = "feedermini/desiccant_reset"
    FRESH_ELEMENT_DESICCANT_RESET = "feeder/desiccant_reset"
    CALL_PET = "callPet"
    CANCEL_FEED = "cancelRealtimeFeed"
    MANUAL_FEED_MINI = "feedermini/save_dailyfeed"
    MANUAL_FEED_FRESH_ELEMENT = "feeder/save_dailyfeed"
    MANUAL_FEED_DUAL = "saveDailyFeed"
    DAILY_FEED_AND_EAT = "dailyFeedAndEat"  # D3
    FEED_STATISTIC = "feedStatistic"  # D4
    DAILY_FEED = "dailyFeeds"  # D4S
    REMOVE_DAILY_FEED = "removeDailyFeed"
    RESTORE_DAILY_FEED = "restoreDailyFeed"
    SAVE_FEED = "saveFeed"  # For Feeding plan
