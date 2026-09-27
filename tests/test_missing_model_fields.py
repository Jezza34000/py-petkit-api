"""Fields the PetKit API returns but the models dropped.

Each key below is the camelCase name the API sends, so a payload carrying it
must populate the matching snake_case attribute.
"""

import unittest

from pypetkitapi.feeder_container import SettingsFeeder, StateFeeder
from pypetkitapi.litter_container import SettingsLitter
from pypetkitapi.water_fountain_container import WaterFountain


class TestFeederFields(unittest.TestCase):
    def test_color_setting_from_camel_case(self):
        # D4 skin colour
        settings = SettingsFeeder(**{"colorSetting": 2})
        self.assertEqual(settings.color_setting, 2)

    def test_feed_tone(self):
        # D4S feeding voice
        settings = SettingsFeeder(**{"feedTone": 1})
        self.assertEqual(settings.feed_tone, 1)

    def test_percent(self):
        # feeder food level
        state = StateFeeder(**{"percent": 40})
        self.assertEqual(state.percent, 40)


class TestLitterFields(unittest.TestCase):
    def test_auto_refresh(self):
        # T3/T4 auto deodorising
        settings = SettingsLitter(**{"autoRefresh": 1})
        self.assertEqual(settings.auto_refresh, 1)


class TestW7hFields(unittest.TestCase):
    def test_drink_and_maintenance_fields(self):
        # returned at top level by w7h/device_detail
        fountain = WaterFountain(
            **{
                "id": 1,
                "sn": "SN1",
                "name": "Fountain",
                "hardware": 1,
                "firmware": "1.0",
                "drinkCount": 12,
                "drinkTimeAvg": 9,
                "nextFlushTime": "2026/09/30 08:00",
                "nextWaterChangeTime": "2026/10/02 08:00",
            }
        )
        self.assertEqual(fountain.drink_count, 12)
        self.assertEqual(fountain.drink_time_avg, 9)
        self.assertEqual(fountain.next_flush_time, "2026/09/30 08:00")
        self.assertEqual(fountain.next_water_change_time, "2026/10/02 08:00")


if __name__ == "__main__":
    unittest.main()
