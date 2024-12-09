"""Constants for the pypetkitapi library."""

from enum import StrEnum

MIN_FEED_AMOUNT = 0
MAX_FEED_AMOUNT = 10

RES_KEY = "result"
ERR_KEY = "error"
SUCCESS_KEY = "success"

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

DEVICES_LITTER_BOX = [T4, T5, T6]
DEVICES_FEEDER = [FEEDER, FEEDER_MINI, D4, D4S, D4H, D4SH]
DEVICES_WATER_FOUNTAIN = [W5, CTW3]
ALL_DEVICES = [*DEVICES_LITTER_BOX, *DEVICES_FEEDER, *DEVICES_WATER_FOUNTAIN]


class PetkitURL(StrEnum):
    """Petkit URL constants"""

    REGION_SRV = "https://passport.petkt.com/v1/regionservers"


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
    TIMEZONE_ID = "Europe/Paris"
    LOCALE = "en-US"
    IMG_VERSION = "1.0"
    HOUR = "24"


CLIENT_NFO = {
    "locale": Header.LOCALE.value,
    "name": Client.MODEL_NAME.value,
    "osVersion": Client.OS_VERSION.value,
    "platform": Client.PLATFORM_TYPE.value,
    "source": Client.SOURCE.value,
    "timezone": Header.TIMEZONE.value,
    "timezoneId": Header.TIMEZONE_ID.value,
    "version": Header.API_VERSION.value,
}

LOGIN_DATA = {
    "client": str(CLIENT_NFO),
    "oldVersion": Header.API_VERSION,
}


class PetkitEndpoint(StrEnum):
    """Petkit Endpoint constants"""

    LOGIN = "user/login"
    GET_LOGIN_CODE = "user/sendcodeforquicklogin"
    REFRESH_SESSION = "user/refreshsession"
    FAMILY_LIST = "group/family/list"
    REFRESH_HOME_V2 = "refreshHomeV2"
    DEVICE_DETAIL = "device_detail"
    DEVICE_DATA = "deviceData"
    GET_DEVICE_RECORD = "getDeviceRecord"
    GET_DEVICE_RECORD_RELEASE = "getDeviceRecordRelease"
    UPDATE_SETTING = "updateSettings"

    # Litter Box
    DEODORANT_RESET = "deodorantReset"
    CONTROL_DEVICE = "controlDevice"

    # Feeders
    REPLENISHED_FOOD = "added"
    FRESH_ELEMENT_CALIBRATION = "food_reset"
    FRESH_ELEMENT_CANCEL_FEED = "cancel_realtime_feed"
    DESICCANT_RESET = "desiccantReset"
    MINI_DESICCANT_RESET = "feedermini/desiccant_reset"
    FRESH_ELEMENT_DESICCANT_RESET = "feeder/desiccant_reset"
    CALL_PET = "callPet"
    CANCEL_FEED = "cancelRealtimeFeed"
    MINI_MANUAL_FEED = "feedermini/save_dailyfeed"
    FRESH_ELEMENT_MANUAL_FEED = "feeder/save_dailyfeed"
    MANUAL_FEED = "saveDailyFeed"
