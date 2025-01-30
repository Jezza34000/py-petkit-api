import unittest

from pypetkitapi.const import PetkitEndpoint, D3, D4, D4S, FEEDER_MINI
from pypetkitapi.containers import Device
from pypetkitapi.feeder_container import (
    Feeder,
    CloudProduct,
    MultiFeedItem,
    FeederRecord,
)
from pydantic import ValidationError

fake_feeder_data = {
    "result": {
        "autoUpgrade": 1,
        "btMac": "a0b1c2d3e4a5",
        "cloudProduct": {
            "chargeType": "CHARGE",
            "name": "Basic Annual Auto-renewal",
            "serviceId": 4076,
            "subscribe": 1,
            "workIndate": 1762901999,
            "workTime": 1707391770,
        },
        "createdAt": "2024-06-24T13:21:58.067+0000",
        "firmware": "733",
        "firmwareDetails": [
            {"module": "app", "version": 244501},
            {"module": "alg", "version": 244314},
            {"module": "audio", "version": 244316},
            {"module": "kernel", "version": 231201},
            {"module": "rootfs", "version": 233101},
            {"module": "ble", "version": 136},
        ],
        "freeCareInfo": {
            "freeBubble": "https://domain.com/img.png",
            "freeButton": "Get it for free",
            "freeChance": 0,
            "freeDetail": "7-day free trial of HD Playback",
        },
        "hardware": 1,
        "id": 900009999,
        "locale": "Europe/Paris",
        "mac": "a0b1c2d3e4a5",
        "modelCode": 0,
        "multiFeedItem": {
            "feedDailyList": [
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 1,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 2,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 3,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 4,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 5,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 6,
                    "suspended": 0,
                },
                {
                    "items": [
                        {
                            "amount1": 0,
                            "amount2": 1,
                            "id": "18000",
                            "name": "R1",
                            "time": 18000,
                        },
                        {
                            "amount1": 1,
                            "amount2": 0,
                            "id": "25200",
                            "name": "R3",
                            "time": 25200,
                        },
                    ],
                    "repeats": 7,
                    "suspended": 0,
                },
            ],
            "isExecuted": 1,
            "userId": "1",
        },
        "name": "YumShare",
        "relation": {"userId": "100885522"},
        "secret": "9999999999999999",
        "serviceStatus": 1,
        "settings": {
            "attireId": -1,
            "attireSwitch": 1,
            "autoProduct": 1,
            "bucketName1": "01 hopper",
            "bucketName2": "02 hopper",
            "camera": 1,
            "cameraConfig": 2,
            "cameraMultiNew": [
                {"enable": 1, "rpt": "1,2,3,4,5,6,7", "time": [[210, 1290]]}
            ],
            "cameraMultiRange": [],
            "conservation": 0,
            "controlSettings": 3,
            "desiccantNotify": 1,
            "detectConfig": 1,
            "detectInterval": 0,
            "detectMultiRange": [],
            "eatDetection": 1,
            "eatNotify": 0,
            "eatSensitivity": 2,
            "eatVideo": 1,
            "feedNotify": 0,
            "feedPicture": 1,
            "feedSound": 1,
            "foodNotify": 1,
            "foodWarn": 0,
            "foodWarnRange": [480, 1200],
            "highlight": 0,
            "lightConfig": 1,
            "lightMode": 0,
            "lightMultiRange": [[360, 1320]],
            "liveEncrypt": 1,
            "lowBatteryNotify": 1,
            "manualLock": 0,
            "microphone": 0,
            "moveDetection": 0,
            "moveNotify": 0,
            "moveSensitivity": 1,
            "night": 1,
            "numLimit": 5,
            "petDetection": 1,
            "petNotify": 0,
            "petSensitivity": 2,
            "preLive": 1,
            "selectedSound": -1,
            "smartFrame": 0,
            "soundEnable": 0,
            "surplusControl": 1,
            "surplusStandard": 1,
            "systemSoundEnable": 0,
            "timeDisplay": 1,
            "toneConfig": 2,
            "toneMode": 1,
            "toneMultiRange": [[1260, 420]],
            "upload": 1,
            "volume": 3,
        },
        "shareOpen": 0,
        "signupAt": "2024-01-12T12:12:12.873+0000",
        "sn": "20252220DA0000",
        "state": {
            "batteryPower": 4,
            "batteryStatus": 0,
            "bowl": -1,
            "cameraStatus": 1,
            "conservationStatus": 0,
            "desiccantLeftDays": 29,
            "desiccantTime": 0,
            "door": 1,
            "eating": 0,
            "feedState": {
                "addAmountTotal1": 0,
                "addAmountTotal2": 0,
                "eatAvg": 216,
                "eatCount": 6,
                "eatTimes": [18157, 18454, 25507, 29156, 32672, 32789],
                "feedTimes": {
                    "18000": 1,
                    "25200": 3,
                },
                "planAmountTotal1": 4,
                "planAmountTotal2": 6,
                "planRealAmountTotal1": 1,
                "planRealAmountTotal2": 3,
                "realAmountTotal1": 1,
                "realAmountTotal2": 3,
                "times": 4,
            },
            "feeding": 0,
            "food1": 2,
            "food2": 2,
            "ota": 0,
            "overall": 1,
            "pim": 1,
            "runtime": 0,
            "wifi": {"bssid": "a0b1c2d3e4a5", "rsq": -50, "ssid": "wifi-network"},
        },
        "timezone": 1.0,
        "user": {
            "avatar": "https://domain.com/img.png",
            "gender": 3,
            "genderCustom": "",
            "id": "100000011",
            "nick": "UserTest",
            "point": {
                "endGrowth": 50,
                "growth": 15,
                "honour": "LV0",
                "icon": "https://domain.com/img.png",
                "icon2": "https://domain.com/img.png",
                "rank": 0,
                "startGrowth": 0,
            },
        },
    }
}


class TestFeederModel(unittest.TestCase):
    """Tests for the Feeder model."""

    def test_feeder_creation(self):
        """Test the creation of Feeder instances from fake data."""
        feeder_data = fake_feeder_data["result"]
        feeder = Feeder(**feeder_data)
        self.assertIsInstance(feeder, Feeder)
        self.assertEqual(feeder.id, feeder_data["id"])
        self.assertEqual(feeder.name, feeder_data["name"])

    def test_feeder_cloud_product(self):
        """Test the cloud product data within the Feeder instances."""
        feeder_data = fake_feeder_data["result"]
        feeder = Feeder(**feeder_data)
        self.assertIsInstance(feeder.cloud_product, CloudProduct)
        self.assertEqual(
            feeder.cloud_product.service_id, feeder_data["cloudProduct"]["serviceId"]
        )

    def test_invalid_feeder_data(self):
        """Test the validation error for invalid feeder data."""
        invalid_data = fake_feeder_data["result"].copy()
        invalid_data["id"] = "invalid_id"  # Invalid data type
        try:
            Feeder(**invalid_data)
        except ValidationError as e:
            self.assertIn("id", str(e))
        else:
            self.fail("ValidationError not raised")

    def test_get_endpoint_feeder(self):
        """Test the get_endpoint method of the Feeder class."""
        device_type = "any_device_type"
        expected_endpoint = PetkitEndpoint.DEVICE_DETAIL
        self.assertEqual(Feeder.get_endpoint(device_type), expected_endpoint)

    def test_query_param_feeder(self):
        """Test the query_param method of the Feeder class."""
        device = Device(
            createdAt=1672531200,
            deviceId=12345,
            deviceName="example_device",
            deviceType="any_device_type",
            groupId=1,
            type=1,
            typeCode=0,
            uniqueId="unique_12345",
        )
        expected_params = {"id": 12345}
        self.assertEqual(Feeder.query_param(device), expected_params)

    def test_get_endpoint_feeder_record(self):
        """Test the get_endpoint method of the FeederRecord class."""
        self.assertEqual(
            FeederRecord.get_endpoint(D3), PetkitEndpoint.DAILY_FEED_AND_EAT
        )
        self.assertEqual(FeederRecord.get_endpoint(D4), PetkitEndpoint.FEED_STATISTIC)
        self.assertEqual(FeederRecord.get_endpoint(D4S), PetkitEndpoint.DAILY_FEED)
        self.assertEqual(
            FeederRecord.get_endpoint(FEEDER_MINI), PetkitEndpoint.DAILY_FEED.lower()
        )
        self.assertEqual(
            FeederRecord.get_endpoint("unknown_type"), PetkitEndpoint.GET_DEVICE_RECORD
        )

    def test_query_param_feeder_record(self):
        """Test the query_param method of the FeederRecord class."""
        device = Device(
            createdAt=1672531200,
            deviceId=12345,
            deviceName="example_device",
            deviceType="d4",
            groupId=1,
            type=1,
            typeCode=0,
            uniqueId="unique_12345",
        )
        request_date = "20240101"
        expected_params = {"date": request_date, "type": 0, "deviceId": 12345}
        self.assertEqual(
            FeederRecord.query_param(device, request_date=request_date), expected_params
        )

        device.device_type = "other_type"
        expected_params = {"days": request_date, "deviceId": 12345}
        self.assertEqual(
            FeederRecord.query_param(device, request_date=request_date), expected_params
        )


if __name__ == "__main__":
    unittest.main()
