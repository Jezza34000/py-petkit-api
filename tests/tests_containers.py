"""Tests for pypetkit.containers"""

from pypetkit.containers import (
    AccountData,
    CloudProduct,
    Device,
    FirmwareDetail,
    Pet,
    RegionInfo,
    SessionInfo,
    User,
    Wifi,
)
from pypetkit.feeder_container import (
    CameraMultiNew,
    EventState,
    FeedDailyList,
    Feeder,
    FeederRecord,
    FeedItem,
    FeedState,
    MultiFeedItem,
    SettingsFeeder,
    StateFeeder,
)
from pypetkit.litter_container import Litter, SettingsLitter, StateLitter
from pypetkit.water_fountain_container import (
    WaterFountain,
    Electricity,
    Type,
    Schedule,
    SettingsFountain,
    Status,
)


def test_region_info():
    data = {"accountType": "type1", "gateway": "gateway1", "id": "id1", "name": "name1"}
    region_info = RegionInfo(**data)
    assert region_info.account_type == "type1"
    assert region_info.gateway == "gateway1"
    assert region_info.id == "id1"
    assert region_info.name == "name1"


def test_session_info():
    data = {
        "id": "session1",
        "userId": "user1",
        "expiresIn": 3600,
        "region": "region1",
        "createdAt": "2023-01-01T00:00:00Z",
    }
    session_info = SessionInfo(**data)
    assert session_info.id == "session1"
    assert session_info.user_id == "user1"
    assert session_info.expires_in == 3600
    assert session_info.region == "region1"
    assert session_info.created_at == "2023-01-01T00:00:00Z"


def test_device():
    data = {
        "createdAt": 1234567890,
        "deviceId": 1,
        "deviceName": "Device1",
        "deviceType": "Type1",
        "groupId": 1,
        "type": 1,
        "typeCode": 1,
        "uniqueId": "unique1",
    }
    device = Device(**data)
    assert device.created_at == 1234567890
    assert device.device_id == 1
    assert device.device_name == "Device1"
    assert device.device_type == "Type1"
    assert device.group_id == 1
    assert device.type == 1
    assert device.type_code == 1
    assert device.unique_id == "unique1"


def test_pet():
    data = {"avatar": "avatar1", "createdAt": 1234567890, "petId": 1, "petName": "Pet1"}
    pet = Pet(**data)
    assert pet.avatar == "avatar1"
    assert pet.created_at == 1234567890
    assert pet.pet_id == 1
    assert pet.pet_name == "Pet1"


def test_user():
    data = {
        "avatar": "avatar1",
        "createdAt": 1234567890,
        "isOwner": 1,
        "userId": 1,
        "userName": "User1",
    }
    user = User(**data)
    assert user.avatar == "avatar1"
    assert user.created_at == 1234567890
    assert user.is_owner == 1
    assert user.user_id == 1
    assert user.user_name == "User1"


def test_account_data():
    data = {
        "deviceList": [],
        "expired": False,
        "groupId": 1,
        "name": "Account1",
        "owner": 1,
        "petList": [],
        "userList": [],
    }
    account_data = AccountData(**data)
    assert account_data.device_list == []
    assert account_data.expired == False
    assert account_data.group_id == 1
    assert account_data.name == "Account1"
    assert account_data.owner == 1
    assert account_data.pet_list == []
    assert account_data.user_list == []


def test_cloud_product():
    data = {
        "chargeType": "type1",
        "name": "Product1",
        "serviceId": 1,
        "subscribe": 1,
        "workIndate": 1234567890,
        "workTime": 1234567890,
    }
    cloud_product = CloudProduct(**data)
    assert cloud_product.charge_type == "type1"
    assert cloud_product.name == "Product1"
    assert cloud_product.service_id == 1
    assert cloud_product.subscribe == 1
    assert cloud_product.work_indate == 1234567890
    assert cloud_product.work_time == 1234567890


def test_wifi():
    data = {"bssid": "bssid1", "rsq": 1, "ssid": "ssid1"}
    wifi = Wifi(**data)
    assert wifi.bssid == "bssid1"
    assert wifi.rsq == 1
    assert wifi.ssid == "ssid1"


def test_firmware_detail():
    data = {"module": "module1", "version": 1}
    firmware_detail = FirmwareDetail(**data)
    assert firmware_detail.module == "module1"
    assert firmware_detail.version == 1


def test_feed_item():
    data = {
        "id": "item1",
        "name": "FeedItem1",
        "time": 1234567890,
        "amount": 100,
        "amount1": 50,
        "amount2": 50,
    }
    feed_item = FeedItem(**data)
    assert feed_item.id == "item1"
    assert feed_item.name == "FeedItem1"
    assert feed_item.time == 1234567890
    assert feed_item.amount == 100
    assert feed_item.amount1 == 50
    assert feed_item.amount2 == 50


def test_feed_daily_list():
    data = {"items": [], "repeats": 1, "suspended": 0}
    feed_daily_list = FeedDailyList(**data)
    assert feed_daily_list.items == []
    assert feed_daily_list.repeats == 1
    assert feed_daily_list.suspended == 0


def test_multi_feed_item():
    data = {"feedDailyList": [], "isExecuted": 1, "userId": "user1"}
    multi_feed_item = MultiFeedItem(**data)
    assert multi_feed_item.feed_daily_list == []
    assert multi_feed_item.is_executed == 1
    assert multi_feed_item.user_id == "user1"


def test_camera_multi_new():
    data = {"enable": 1, "rpt": "rpt1", "time": [(1, 2), (3, 4)]}
    camera_multi_new = CameraMultiNew(**data)
    assert camera_multi_new.enable == 1
    assert camera_multi_new.rpt == "rpt1"
    assert camera_multi_new.time == [(1, 2), (3, 4)]


def test_settings_feeder():
    data = {
        "attireId": 1,
        "attireSwitch": 1,
        "autoProduct": 1,
        "camera": 1,
        "cameraConfig": 1,
        "cameraMultiRange": [],
        "controlSettings": 1,
        "desiccantNotify": 1,
        "detectConfig": 1,
        "detectInterval": 1,
        "detectMultiRange": [],
        "eatDetection": 1,
        "eatNotify": 1,
        "eatSensitivity": 1,
        "eatVideo": 1,
        "feedNotify": 1,
        "feedPicture": 1,
        "foodNotify": 1,
        "foodWarn": 1,
        "foodWarnRange": [1, 2],
        "highlight": 1,
        "lightConfig": 1,
        "lightMode": 1,
        "lightMultiRange": [(1, 2)],
        "liveEncrypt": 1,
        "lowBatteryNotify": 1,
        "manualLock": 1,
        "microphone": 1,
        "moveDetection": 1,
        "moveNotify": 1,
        "moveSensitivity": 1,
        "night": 1,
        "numLimit": 1,
        "petDetection": 1,
        "petNotify": 1,
        "petSensitivity": 1,
        "preLive": 1,
        "selectedSound": 1,
        "smartFrame": 1,
        "soundEnable": 1,
        "surplusControl": 1,
        "surplusStandard": 1,
        "systemSoundEnable": 1,
        "timeDisplay": 1,
        "toneConfig": 1,
        "toneMode": 1,
        "toneMultiRange": [(1, 2)],
        "upload": 1,
        "volume": 1,
        "feedSound": 1,
        "factor": 1,
        "colorSetting": 1,
        "conservation": 1,
        "bucketName1": "bucket1",
        "bucketName2": "bucket2",
        "cameraMultiNew": [],
    }
    settings_feeder = SettingsFeeder(**data)
    assert settings_feeder.attire_id == 1
    assert settings_feeder.attire_switch == 1
    assert settings_feeder.auto_product == 1
    assert settings_feeder.camera == 1
    assert settings_feeder.camera_config == 1
    assert settings_feeder.camera_multi_range == []
    assert settings_feeder.control_settings == 1
    assert settings_feeder.desiccant_notify == 1
    assert settings_feeder.detect_config == 1
    assert settings_feeder.detect_interval == 1
    assert settings_feeder.detect_multi_range == []
    assert settings_feeder.eat_detection == 1
    assert settings_feeder.eat_notify == 1
    assert settings_feeder.eat_sensitivity == 1
    assert settings_feeder.eat_video == 1
    assert settings_feeder.feed_notify == 1
    assert settings_feeder.feed_picture == 1
    assert settings_feeder.food_notify == 1
    assert settings_feeder.food_warn == 1
    assert settings_feeder.food_warn_range == [1, 2]
    assert settings_feeder.highlight == 1
    assert settings_feeder.light_config == 1
    assert settings_feeder.light_mode == 1
    assert settings_feeder.light_multi_range == [(1, 2)]
    assert settings_feeder.live_encrypt == 1
    assert settings_feeder.low_battery_notify == 1
    assert settings_feeder.manual_lock == 1
    assert settings_feeder.microphone == 1
    assert settings_feeder.move_detection == 1
    assert settings_feeder.move_notify == 1
    assert settings_feeder.move_sensitivity == 1
    assert settings_feeder.night == 1
    assert settings_feeder.num_limit == 1
    assert settings_feeder.pet_detection == 1
    assert settings_feeder.pet_notify == 1
    assert settings_feeder.pet_sensitivity == 1
    assert settings_feeder.pre_live == 1
    assert settings_feeder.selected_sound == 1
    assert settings_feeder.smart_frame == 1
    assert settings_feeder.sound_enable == 1
    assert settings_feeder.surplus_control == 1
    assert settings_feeder.surplus_standard == 1
    assert settings_feeder.system_sound_enable == 1
    assert settings_feeder.time_display == 1
    assert settings_feeder.tone_config == 1
    assert settings_feeder.tone_mode == 1
    assert settings_feeder.tone_multi_range == [(1, 2)]
    assert settings_feeder.upload == 1
    assert settings_feeder.volume == 1
    assert settings_feeder.feed_sound == 1
    assert settings_feeder.factor == 1
    assert settings_feeder.color_setting == 1
    assert settings_feeder.conservation == 1
    assert settings_feeder.bucket_name1 == "bucket1"
    assert settings_feeder.bucket_name2 == "bucket2"
    assert settings_feeder.camera_multi_new == []


def test_feed_state():
    data = {
        "eatAvg": 1,
        "eatCount": 1,
        "eatTimes": [1, 2],
        "feedTimes": {},
        "times": 1,
        "addAmountTotal": 1,
        "planAmountTotal": 1,
        "planRealAmountTotal": 1,
        "realAmountTotal": 1,
        "addAmountTotal1": 1,
        "addAmountTotal2": 1,
        "planAmountTotal1": 1,
        "planAmountTotal2": 1,
        "planRealAmountTotal1": 1,
        "planRealAmountTotal2": 1,
        "realAmountTotal1": 1,
        "realAmountTotal2": 1,
    }
    feed_state = FeedState(**data)
    assert feed_state.eat_avg == 1
    assert feed_state.eat_count == 1
    assert feed_state.eat_times == [1, 2]
    assert feed_state.feed_times == {}
    assert feed_state.times == 1
    assert feed_state.add_amount_total == 1
    assert feed_state.plan_amount_total == 1
    assert feed_state.plan_real_amount_total == 1
    assert feed_state.real_amount_total == 1
    assert feed_state.add_amount_total1 == 1
    assert feed_state.add_amount_total2 == 1
    assert feed_state.plan_amount_total1 == 1
    assert feed_state.plan_amount_total2 == 1
    assert feed_state.plan_real_amount_total1 == 1
    assert feed_state.plan_real_amount_total2 == 1
    assert feed_state.real_amount_total1 == 1
    assert feed_state.real_amount_total2 == 1


def test_state_feeder():
    data = {
        "batteryPower": 1,
        "batteryStatus": 1,
        "bowl": 1,
        "cameraStatus": 1,
        "desiccantLeftDays": 1,
        "desiccantTime": 1,
        "door": 1,
        "feedState": None,
        "feeding": 1,
        "ota": 1,
        "overall": 1,
        "pim": 1,
        "runtime": 1,
        "wifi": None,
        "eating": 1,
        "food": 1,
        "food1": 1,
        "food2": 1,
        "conservationStatus": 1,
    }
    state_feeder = StateFeeder(**data)
    assert state_feeder.battery_power == 1
    assert state_feeder.battery_status == 1
    assert state_feeder.bowl == 1
    assert state_feeder.camera_status == 1
    assert state_feeder.desiccant_left_days == 1
    assert state_feeder.desiccant_time == 1
    assert state_feeder.door == 1
    assert state_feeder.feed_state is None
    assert state_feeder.feeding == 1
    assert state_feeder.ota == 1
    assert state_feeder.overall == 1
    assert state_feeder.pim == 1
    assert state_feeder.runtime == 1
    assert state_feeder.wifi is None
    assert state_feeder.eating == 1
    assert state_feeder.food == 1
    assert state_feeder.food1 == 1
    assert state_feeder.food2 == 1
    assert state_feeder.conservation_status == 1


def test_feeder():
    data = {
        "autoUpgrade": 1,
        "btMac": "mac1",
        "cloudProduct": None,
        "createdAt": "2023-01-01T00:00:00Z",
        "firmware": "firmware1",
        "firmwareDetails": [],
        "hardware": 1,
        "id": 1,
        "locale": "locale1",
        "mac": "mac1",
        "modelCode": 1,
        "multiFeedItem": None,
        "name": "Feeder1",
        "secret": "secret1",
        "serviceStatus": 1,
        "settings": None,
        "shareOpen": 1,
        "signupAt": "2023-01-01T00:00:00Z",
        "sn": "sn1",
        "state": None,
        "timezone": 1.0,
        "p2pType": 1,
        "multiConfig": True,
        "deviceType": "type1",
    }
    feeder = Feeder(**data)
    assert feeder.auto_upgrade == 1
    assert feeder.bt_mac == "mac1"
    assert feeder.cloud_product is None
    assert feeder.created_at == "2023-01-01T00:00:00Z"
    assert feeder.firmware == "firmware1"
    assert feeder.firmware_details == []
    assert feeder.hardware == 1
    assert feeder.id == 1
    assert feeder.locale == "locale1"
    assert feeder.mac == "mac1"
    assert feeder.model_code == 1
    assert feeder.multi_feed_item is None
    assert feeder.name == "Feeder1"
    assert feeder.secret == "secret1"
    assert feeder.service_status == 1
    assert feeder.settings is None
    assert feeder.share_open == 1
    assert feeder.signup_at == "2023-01-01T00:00:00Z"
    assert feeder.sn == "sn1"
    assert feeder.state is None
    assert feeder.timezone == 1.0
    assert feeder.p2p_type == 1
    assert feeder.multi_config is True
    assert feeder.device_type == "type1"


def test_event_state():
    data = {
        "completedAt": "2023-01-01T00:00:00Z",
        "errCode": 1,
        "media": 1,
        "realAmount1": 1,
        "realAmount2": 1,
        "result": 1,
        "surplusStandard": 1,
    }
    event_state = EventState(**data)
    assert event_state.completed_at == "2023-01-01T00:00:00Z"
    assert event_state.err_code == 1
    assert event_state.media == 1
    assert event_state.real_amount1 == 1
    assert event_state.real_amount2 == 1
    assert event_state.result == 1
    assert event_state.surplus_standard == 1


def test_feeder_record():
    data = {
        "aesKey": "key1",
        "duration": 1,
        "eventId": "event1",
        "expire": 1,
        "mark": 1,
        "mediaApi": "api1",
        "startTime": 1,
        "storageSpace": 1,
        "eatVideo": 1,
        "isNeedUploadVideo": 1,
        "preview": "preview1",
        "time": 1,
        "timestamp": 1,
        "aesKey1": "key1",
        "aesKey2": "key2",
        "amount1": 1,
        "amount2": 1,
        "completedAt": 1,
        "content": {},
        "desc": "desc1",
        "deviceId": 1,
        "eatEndTime": 1,
        "eatStartTime": 1,
        "empty": 1,
        "endTime": 1,
        "enumEventType": "type1",
        "event": "event1",
        "eventType": 1,
        "expire1": 1,
        "expire2": 1,
        "id": "id1",
        "isExecuted": 1,
        "mediaList": [],
        "name": "name1",
        "preview1": "preview1",
        "preview2": "preview2",
        "src": 1,
        "state": None,
        "status": 1,
    }
    feeder_record = FeederRecord(**data)
    assert feeder_record.aes_key == "key1"
    assert feeder_record.duration == 1
    assert feeder_record.event_id == "event1"
    assert feeder_record.expire == 1
    assert feeder_record.mark == 1
    assert feeder_record.media_api == "api1"
    assert feeder_record.start_time == 1
    assert feeder_record.storage_space == 1
    assert feeder_record.eat_video == 1
    assert feeder_record.is_need_upload_video == 1
    assert feeder_record.preview == "preview1"
    assert feeder_record.time == 1
    assert feeder_record.timestamp == 1
    assert feeder_record.aes_key1 == "key1"
    assert feeder_record.aes_key2 == "key2"
    assert feeder_record.amount1 == 1
    assert feeder_record.amount2 == 1
    assert feeder_record.completed_at == 1
    assert feeder_record.content == {}
    assert feeder_record.desc == "desc1"
    assert feeder_record.device_id == 1
    assert feeder_record.eat_end_time == 1
    assert feeder_record.eat_start_time == 1
    assert feeder_record.empty == 1
    assert feeder_record.end_time == 1
    assert feeder_record.enum_event_type == "type1"
    assert feeder_record.event == "event1"
    assert feeder_record.event_type == 1
    assert feeder_record.expire1 == 1
    assert feeder_record.expire2 == 1
    assert feeder_record.id == "id1"
    assert feeder_record.is_executed == 1
    assert feeder_record.media_list == []
    assert feeder_record.name == "name1"
    assert feeder_record.preview1 == "preview1"
    assert feeder_record.preview2 == "preview2"
    assert feeder_record.src == 1
    assert feeder_record.state is None
    assert feeder_record.status == 1


def test_settings_litter():
    data = {
        "autoIntervalMin": 10,
        "autoWork": 1,
        "avoidRepeat": 1,
        "bury": 1,
        "controlSettings": 1,
        "deepClean": 1,
        "deepRefresh": 1,
        "deodorantNotify": 1,
        "distrubMultiRange": [[1, 2], [3, 4]],
        "disturbConfig": 1,
        "disturbMode": 1,
        "disturbRange": [1, 2],
        "downpos": 1,
        "dumpSwitch": 1,
        "fixedTimeClear": 1,
        "kitten": 1,
        "kittenPercent": 0.5,
        "kittenTipsTime": 1,
        "lackLiquidNotify": 1,
        "lackSandNotify": 1,
        "language": "en",
        "languageFollow": 1,
        "languages": ["en", "fr"],
        "lightConfig": 1,
        "lightMode": 1,
        "lightMultiRange": [[1, 2]],
        "lightRange": [1, 2],
        "lightest": 1,
        "litterFullNotify": 1,
        "manualLock": 1,
        "petInNotify": 1,
        "relateK3Switch": 1,
        "sandType": 1,
        "softMode": 1,
        "stillTime": 1,
        "stopTime": 1,
        "underweight": 1,
        "unit": 1,
        "weightPopup": 1,
        "workNotify": 1,
        "autoProduct": 1,
        "camera": 1,
        "cameraConfig": 1,
        "cleanningNotify": 1,
        "garbageNotify": 1,
        "highlight": 1,
        "lightAssist": 1,
        "liveEncrypt": 1,
        "microphone": 1,
        "moveNotify": 1,
        "night": 1,
        "packageStandard": [1, 2],
        "petDetection": 1,
        "petNotify": 1,
        "preLive": 1,
        "systemSoundEnable": 1,
        "timeDisplay": 1,
        "toiletDetection": 1,
        "toiletNotify": 1,
        "toneConfig": 1,
        "toneMode": 1,
        "toneMultiRange": [[1, 2]],
        "tumbling": 1,
        "upload": 1,
        "volume": 1,
        "wanderDetection": 1,
    }
    settings_litter = SettingsLitter(**data)
    assert settings_litter.auto_interval_min == 10
    assert settings_litter.auto_work == 1
    assert settings_litter.avoid_repeat == 1
    assert settings_litter.bury == 1
    assert settings_litter.control_settings == 1
    assert settings_litter.deep_clean == 1
    assert settings_litter.deep_refresh == 1
    assert settings_litter.deodorant_notify == 1
    assert settings_litter.distrub_multi_range == [[1, 2], [3, 4]]
    assert settings_litter.disturb_config == 1
    assert settings_litter.disturb_mode == 1
    assert settings_litter.disturb_range == [1, 2]
    assert settings_litter.downpos == 1
    assert settings_litter.dump_switch == 1
    assert settings_litter.fixed_time_clear == 1
    assert settings_litter.kitten == 1
    assert settings_litter.kitten_percent == 0.5
    assert settings_litter.kitten_tips_time == 1
    assert settings_litter.lack_liquid_notify == 1
    assert settings_litter.lack_sand_notify == 1
    assert settings_litter.language == "en"
    assert settings_litter.language_follow == 1
    assert settings_litter.languages == ["en", "fr"]
    assert settings_litter.light_config == 1
    assert settings_litter.light_mode == 1
    assert settings_litter.light_multi_range == [[1, 2]]
    assert settings_litter.light_range == [1, 2]
    assert settings_litter.lightest == 1
    assert settings_litter.litter_full_notify == 1
    assert settings_litter.manual_lock == 1
    assert settings_litter.pet_in_notify == 1
    assert settings_litter.relate_k3_switch == 1
    assert settings_litter.sand_type == 1
    assert settings_litter.soft_mode == 1
    assert settings_litter.still_time == 1
    assert settings_litter.stop_time == 1
    assert settings_litter.underweight == 1
    assert settings_litter.unit == 1
    assert settings_litter.weight_popup == 1
    assert settings_litter.work_notify == 1
    assert settings_litter.auto_product == 1
    assert settings_litter.camera == 1
    assert settings_litter.camera_config == 1
    assert settings_litter.cleanning_notify == 1
    assert settings_litter.garbage_notify == 1
    assert settings_litter.highlight == 1
    assert settings_litter.light_assist == 1
    assert settings_litter.live_encrypt == 1
    assert settings_litter.microphone == 1
    assert settings_litter.move_notify == 1
    assert settings_litter.night == 1
    assert settings_litter.package_standard == [1, 2]
    assert settings_litter.pet_detection == 1
    assert settings_litter.pet_notify == 1
    assert settings_litter.pre_live == 1
    assert settings_litter.system_sound_enable == 1
    assert settings_litter.time_display == 1
    assert settings_litter.toilet_detection == 1
    assert settings_litter.toilet_notify == 1
    assert settings_litter.tone_config == 1
    assert settings_litter.tone_mode == 1
    assert settings_litter.tone_multi_range == [[1, 2]]
    assert settings_litter.tumbling == 1
    assert settings_litter.upload == 1
    assert settings_litter.volume == 1
    assert settings_litter.wander_detection == 1


def test_state_litter():
    data = {
        "box": 1,
        "boxFull": True,
        "boxState": 1,
        "deodorantLeftDays": 10,
        "frequentRestroom": 1,
        "liquidEmpty": True,
        "liquidLack": True,
        "liquidReset": 1,
        "lowPower": True,
        "offlineTime": 1,
        "ota": 1,
        "overall": 1,
        "petError": True,
        "petInTime": 1,
        "pim": 1,
        "power": 1,
        "sandCorrect": 1,
        "sandLack": True,
        "sandPercent": 50,
        "sandStatus": 1,
        "sandType": 1,
        "sandWeight": 1,
        "usedTimes": 1,
        "wifi": None,
        "baggingState": 1,
        "battery": 1,
        "boxStoreState": 1,
        "cameraStatus": 1,
        "dumpState": 1,
        "liquid": 1,
        "packState": 1,
        "packageInstall": 1,
        "packageSecret": "secret",
        "packageSn": "sn",
        "packageState": 1,
        "piIns": 1,
        "purificationLeftDays": 1,
        "sealDoorState": 1,
        "topIns": 1,
        "wanderTime": 1,
    }
    state_litter = StateLitter(**data)
    assert state_litter.box == 1
    assert state_litter.box_full is True
    assert state_litter.box_state == 1
    assert state_litter.deodorant_left_days == 10
    assert state_litter.frequent_restroom == 1
    assert state_litter.liquid_empty is True
    assert state_litter.liquid_lack is True
    assert state_litter.liquid_reset == 1
    assert state_litter.low_power is True
    assert state_litter.offline_time == 1
    assert state_litter.ota == 1
    assert state_litter.overall == 1
    assert state_litter.pet_error is True
    assert state_litter.pet_in_time == 1
    assert state_litter.pim == 1
    assert state_litter.power == 1
    assert state_litter.sand_correct == 1
    assert state_litter.sand_lack is True
    assert state_litter.sand_percent == 50
    assert state_litter.sand_status == 1
    assert state_litter.sand_type == 1
    assert state_litter.sand_weight == 1
    assert state_litter.used_times == 1
    assert state_litter.wifi is None
    assert state_litter.bagging_state == 1
    assert state_litter.battery == 1
    assert state_litter.box_store_state == 1
    assert state_litter.camera_status == 1
    assert state_litter.dump_state == 1
    assert state_litter.liquid == 1
    assert state_litter.pack_state == 1
    assert state_litter.package_install == 1
    assert state_litter.package_secret == "secret"
    assert state_litter.package_sn == "sn"
    assert state_litter.package_state == 1
    assert state_litter.pi_ins == 1
    assert state_litter.purification_left_days == 1
    assert state_litter.seal_door_state == 1
    assert state_litter.top_ins == 1
    assert state_litter.wander_time == 1


def test_litter():
    data = {
        "autoUpgrade": 1,
        "btMac": "mac1",
        "createdAt": "2023-01-01T00:00:00Z",
        "firmware": "firmware1",
        "firmwareDetails": [],
        "hardware": 1,
        "id": 1,
        "isPetOutTips": 1,
        "locale": "locale1",
        "mac": "mac1",
        "maintenanceTime": 1,
        "multiConfig": True,
        "name": "Litter1",
        "petInTipLimit": 1,
        "petOutTips": [],
        "secret": "secret1",
        "settings": None,
        "shareOpen": 1,
        "signupAt": "2023-01-01T00:00:00Z",
        "sn": "sn1",
        "state": None,
        "timezone": 1.0,
        "cloudProduct": None,
        "inTimes": 1,
        "lastOutTime": 1,
        "p2pType": 1,
        "packageIgnoreState": 1,
        "packageTotalCount": 1,
        "packageUsedCount": 1,
        "petOutRecords": [],
        "serviceStatus": 1,
        "totalTime": 1,
        "deviceType": "type1",
    }
    litter = Litter(**data)
    assert litter.auto_upgrade == 1
    assert litter.bt_mac == "mac1"
    assert litter.created_at == "2023-01-01T00:00:00Z"
    assert litter.firmware == "firmware1"
    assert litter.firmware_details == []
    assert litter.hardware == 1
    assert litter.id == 1
    assert litter.is_pet_out_tips == 1
    assert litter.locale == "locale1"
    assert litter.mac == "mac1"
    assert litter.maintenance_time == 1
    assert litter.multi_config is True
    assert litter.name == "Litter1"
    assert litter.pet_in_tip_limit == 1
    assert litter.pet_out_tips == []
    assert litter.secret == "secret1"
    assert litter.settings is None
    assert litter.share_open == 1
    assert litter.signup_at == "2023-01-01T00:00:00Z"
    assert litter.sn == "sn1"
    assert litter.state is None
    assert litter.timezone == 1.0
    assert litter.cloud_product is None
    assert litter.in_times == 1
    assert litter.last_out_time == 1
    assert litter.p2p_type == 1
    assert litter.package_ignore_state == 1
    assert litter.package_total_count == 1
    assert litter.package_used_count == 1
    assert litter.pet_out_records == []
    assert litter.service_status == 1
    assert litter.total_time == 1
    assert litter.device_type == "type1"


def test_water_fountain_initialization():
    data = {
        "breakdownWarning": 1,
        "createdAt": "2023-01-01T00:00:00Z",
        "electricity": {
            "batteryPercent": 50,
            "batteryVoltage": 12,
            "supplyVoltage": 220,
        },
        "expectedCleanWater": 100,
        "expectedUseElectricity": 10.5,
        "filterExpectedDays": 30,
        "filterPercent": 80,
        "filterWarning": 1,
        "firmware": 1,
        "hardware": 1,
        "id": 1,
        "isNightNoDisturbing": 1,
        "lackWarning": 1,
        "locale": "en_US",
        "lowBattery": 1,
        "mac": "00:11:22:33:44:55",
        "mode": 1,
        "moduleStatus": 1,
        "name": "Fountain1",
        "recordAutomaticAddWater": 1,
        "schedule": {
            "alarmBefore": 10,
            "createdAt": "2023-01-01T00:00:00Z",
            "deviceId": "1",
            "deviceType": "CTW3",
            "id": "1",
            "name": "Schedule1",
            "repeat": "daily",
            "status": 1,
            "time": "08:00",
            "type": {
                "enable": 1,
                "id": "1",
                "img": "img.png",
                "isCustom": 1,
                "name": "Type1",
                "priority": 1,
                "withDeviceType": "CTW3",
                "withPet": 1,
            },
            "userCustomId": 1,
        },
        "secret": "secret",
        "settings": {
            "batterySleepTime": 10,
            "batteryWorkingTime": 20,
            "distributionDiagram": 1,
            "disturbConfig": 1,
            "disturbMultiTime": [{"start": "22:00", "end": "06:00"}],
            "lampRingBrightness": 100,
            "lampRingSwitch": 1,
            "lightConfig": 1,
            "lightMultiTime": [{"start": "18:00", "end": "06:00"}],
            "noDisturbingSwitch": 1,
            "smartSleepTime": 10,
            "smartWorkingTime": 20,
        },
        "sn": "SN123456",
        "status": {
            "detectStatus": 1,
            "electricStatus": 1,
            "powerStatus": 1,
            "runStatus": 1,
            "suspendStatus": 1,
        },
        "syncTime": "2023-01-01T00:00:00Z",
        "timezone": 1.0,
        "todayCleanWater": 50,
        "todayPumpRunTime": 100,
        "todayUseElectricity": 5.5,
        "updateAt": "2023-01-01T00:00:00Z",
        "userId": "user123",
        "waterPumpRunTime": 200,
        "deviceType": "CTW3",
    }
    water_fountain = WaterFountain(**data)
    assert water_fountain.breakdown_warning == 1
    assert water_fountain.created_at == "2023-01-01T00:00:00Z"
    assert water_fountain.electricity.battery_percent == 50
    assert water_fountain.electricity.battery_voltage == 12
    assert water_fountain.electricity.supply_voltage == 220
    assert water_fountain.expected_clean_water == 100
    assert water_fountain.expected_use_electricity == 10.5
    assert water_fountain.filter_expected_days == 30
    assert water_fountain.filter_percent == 80
    assert water_fountain.filter_warning == 1
    assert water_fountain.firmware == 1
    assert water_fountain.hardware == 1
    assert water_fountain.id == 1
    assert water_fountain.is_night_no_disturbing == 1
    assert water_fountain.lack_warning == 1
    assert water_fountain.locale == "en_US"
    assert water_fountain.low_battery == 1
    assert water_fountain.mac == "00:11:22:33:44:55"
    assert water_fountain.mode == 1
    assert water_fountain.module_status == 1
    assert water_fountain.name == "Fountain1"
    assert water_fountain.record_automatic_add_water == 1
    assert water_fountain.schedule.alarm_before == 10
    assert water_fountain.schedule.created_at == "2023-01-01T00:00:00Z"
    assert water_fountain.schedule.device_id == "1"
    assert water_fountain.schedule.device_type == "CTW3"
    assert water_fountain.schedule.id == "1"
    assert water_fountain.schedule.name == "Schedule1"
    assert water_fountain.schedule.repeat == "daily"
    assert water_fountain.schedule.status == 1
    assert water_fountain.schedule.time == "08:00"
    assert water_fountain.schedule.type.enable == 1
    assert water_fountain.schedule.type.id == "1"
    assert water_fountain.schedule.type.img == "img.png"
    assert water_fountain.schedule.type.is_custom == 1
    assert water_fountain.schedule.type.name == "Type1"
    assert water_fountain.schedule.type.priority == 1
    assert water_fountain.schedule.type.with_device_type == "CTW3"
    assert water_fountain.schedule.type.with_pet == 1
    assert water_fountain.schedule.user_custom_id == 1
    assert water_fountain.secret == "secret"
    assert water_fountain.settings.battery_sleep_time == 10
    assert water_fountain.settings.battery_working_time == 20
    assert water_fountain.settings.distribution_diagram == 1
    assert water_fountain.settings.disturb_config == 1
    assert water_fountain.settings.disturb_multi_time == [
        {"start": "22:00", "end": "06:00"}
    ]
    assert water_fountain.settings.lamp_ring_brightness == 100
    assert water_fountain.settings.lamp_ring_switch == 1
    assert water_fountain.settings.light_config == 1
    assert water_fountain.settings.light_multi_time == [
        {"start": "18:00", "end": "06:00"}
    ]
    assert water_fountain.settings.no_disturbing_switch == 1
    assert water_fountain.settings.smart_sleep_time == 10
    assert water_fountain.settings.smart_working_time == 20
    assert water_fountain.sn == "SN123456"
    assert water_fountain.status.detect_status == 1
    assert water_fountain.status.electric_status == 1
    assert water_fountain.status.power_status == 1
    assert water_fountain.status.run_status == 1
    assert water_fountain.status.suspend_status == 1
    assert water_fountain.sync_time == "2023-01-01T00:00:00Z"
    assert water_fountain.timezone == 1.0
    assert water_fountain.today_clean_water == 50
    assert water_fountain.today_pump_run_time == 100
    assert water_fountain.today_use_electricity == 5.5
    assert water_fountain.update_at == "2023-01-01T00:00:00Z"
    assert water_fountain.user_id == "user123"
    assert water_fountain.water_pump_run_time == 200
    assert water_fountain.device_type == "CTW3"


def test_electricity():
    data = {"batteryPercent": 50, "batteryVoltage": 12, "supplyVoltage": 220}
    electricity = Electricity(**data)
    assert electricity.battery_percent == 50
    assert electricity.battery_voltage == 12
    assert electricity.supply_voltage == 220


def test_type():
    data = {
        "enable": 1,
        "id": "1",
        "img": "img.png",
        "isCustom": 1,
        "name": "Type1",
        "priority": 1,
        "withDeviceType": "CTW3",
        "withPet": 1,
    }
    type_instance = Type(**data)
    assert type_instance.enable == 1
    assert type_instance.id == "1"
    assert type_instance.img == "img.png"
    assert type_instance.is_custom == 1
    assert type_instance.name == "Type1"
    assert type_instance.priority == 1
    assert type_instance.with_device_type == "CTW3"
    assert type_instance.with_pet == 1


def test_schedule():
    data = {
        "alarmBefore": 10,
        "createdAt": "2023-01-01T00:00:00Z",
        "deviceId": "1",
        "deviceType": "CTW3",
        "id": "1",
        "name": "Schedule1",
        "repeat": "daily",
        "status": 1,
        "time": "08:00",
        "type": {
            "enable": 1,
            "id": "1",
            "img": "img.png",
            "isCustom": 1,
            "name": "Type1",
            "priority": 1,
            "withDeviceType": "CTW3",
            "withPet": 1,
        },
        "userCustomId": 1,
    }
    schedule = Schedule(**data)
    assert schedule.alarm_before == 10
    assert schedule.created_at == "2023-01-01T00:00:00Z"
    assert schedule.device_id == "1"
    assert schedule.device_type == "CTW3"
    assert schedule.id == "1"
    assert schedule.name == "Schedule1"
    assert schedule.repeat == "daily"
    assert schedule.status == 1
    assert schedule.time == "08:00"
    assert schedule.type.enable == 1
    assert schedule.type.id == "1"
    assert schedule.type.img == "img.png"
    assert schedule.type.is_custom == 1
    assert schedule.type.name == "Type1"
    assert schedule.type.priority == 1
    assert schedule.type.with_device_type == "CTW3"
    assert schedule.type.with_pet == 1
    assert schedule.user_custom_id == 1


def test_settings_fountain():
    data = {
        "batterySleepTime": 10,
        "batteryWorkingTime": 20,
        "distributionDiagram": 1,
        "disturbConfig": 1,
        "disturbMultiTime": [{"start": "22:00", "end": "06:00"}],
        "lampRingBrightness": 100,
        "lampRingSwitch": 1,
        "lightConfig": 1,
        "lightMultiTime": [{"start": "18:00", "end": "06:00"}],
        "noDisturbingSwitch": 1,
        "smartSleepTime": 10,
        "smartWorkingTime": 20,
    }
    settings_fountain = SettingsFountain(**data)
    assert settings_fountain.battery_sleep_time == 10
    assert settings_fountain.battery_working_time == 20
    assert settings_fountain.distribution_diagram == 1
    assert settings_fountain.disturb_config == 1
    assert settings_fountain.disturb_multi_time == [{"start": "22:00", "end": "06:00"}]
    assert settings_fountain.lamp_ring_brightness == 100
    assert settings_fountain.lamp_ring_switch == 1
    assert settings_fountain.light_config == 1
    assert settings_fountain.light_multi_time == [{"start": "18:00", "end": "06:00"}]
    assert settings_fountain.no_disturbing_switch == 1
    assert settings_fountain.smart_sleep_time == 10
    assert settings_fountain.smart_working_time == 20


def test_status():
    data = {
        "detectStatus": 1,
        "electricStatus": 1,
        "powerStatus": 1,
        "runStatus": 1,
        "suspendStatus": 1,
    }
    status = Status(**data)
    assert status.detect_status == 1
    assert status.electric_status == 1
    assert status.power_status == 1
    assert status.run_status == 1
    assert status.suspend_status == 1
