"""WaterFountain parsing from real API payloads."""

import unittest

from pypetkitapi.water_fountain_container import WaterFountain

# w5/deviceData from a live W5 (Eversweet), identifiers replaced
W5_DEVICE_DATA = {
    "id": 100000001,
    "mac": "000000000000",
    "secret": "000000000000",
    "userId": "100000000",
    "hardware": 2,
    "firmware": 47,
    "sn": "SN1",
    "name": "Fountain",
    "typeCode": 5,
    "settings": {
        "smartWorkingTime": 3,
        "smartSleepTime": 3,
        "lampRingSwitch": 1,
        "lampRingBrightness": 2,
        "noDisturbingSwitch": 0,
    },
    "voltage": -1,
    "powerStatus": 1,
    "mode": 1,
    "isNightNoDisturbing": 0,
    "breakdownWarning": 0,
    "lackWarning": 0,
    "filterWarning": 0,
    "waterPumpRunTime": 349437,
    "filterPercent": 86,
    "runStatus": 1,
    "todayPumpRunTime": 258,
}


class TestW5Status(unittest.TestCase):
    def test_status_from_top_level_fields(self):
        fountain = WaterFountain(**W5_DEVICE_DATA)
        self.assertIsNotNone(fountain.status)
        self.assertEqual(fountain.status.power_status, 1)
        self.assertEqual(fountain.status.run_status, 1)

    def test_nested_status_is_kept(self):
        data = {**W5_DEVICE_DATA, "status": {"powerStatus": 0, "runStatus": 0}}
        fountain = WaterFountain(**data)
        self.assertEqual(fountain.status.power_status, 0)
        self.assertEqual(fountain.status.run_status, 0)

    def test_no_status_fields(self):
        data = {
            k: v
            for k, v in W5_DEVICE_DATA.items()
            if k not in ("powerStatus", "runStatus")
        }
        self.assertIsNone(WaterFountain(**data).status)


if __name__ == "__main__":
    unittest.main()
