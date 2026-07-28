"""Per-pet meal attribution from feeder records.

The payload shape below is a trimmed copy of a real `getDeviceRecord` response for
a D4SH with pet recognition: `eat[].items[]` carries `petId` for every meal the AI
managed to attribute, and leaves it out for the ones it did not.
"""

import unittest

from pypetkitapi.client import PetKitClient
from pypetkitapi.containers import Device, Pet
from pypetkitapi.feeder_container import Feeder, FeederRecord

# Cipria ate twice, Tali once, and one visit went unrecognised.
FAKE_EAT_RECORD = {
    "eat": [
        {
            "deviceId": 300035322,
            "items": [
                {
                    "eatStartTime": 1753662133,
                    "eatEndTime": 1753662301,
                    "petId": "101401310",
                    "duration": 4,
                },
                {
                    "eatStartTime": 1753662700,
                    "eatEndTime": 1753662838,
                    "petId": "101401320",
                    "duration": 4,
                },
                {
                    "eatStartTime": 1753663000,
                    "eatEndTime": 1753663046,
                    "petId": "101401310",
                    "duration": 4,
                },
                # no petId: the AI did not recognise the cat
                {"eatStartTime": 1753663500, "eatEndTime": 1753663560, "duration": 4},
            ],
        }
    ]
}


def _pet(pet_id: int, name: str) -> Pet:
    return Pet(avatar="", createdAt=0, petId=pet_id, petName=name)


def _feeder() -> Feeder:
    feeder = Feeder(
        id=300035322, name="YumShare", firmware="733", hardware=1, sn="SN0001"
    )
    feeder.device_nfo = Device(
        createdAt=1719234118,
        deviceId=300035322,
        deviceName="yumshare",
        deviceType="d4sh",
        groupId=1,
        type=1,
        uniqueId="u0001",
    )
    feeder.device_records = FeederRecord(**FAKE_EAT_RECORD)
    return feeder


class TestPetFeederStats(unittest.IsolatedAsyncioTestCase):
    """Per-pet feeder stats derived from eat records."""

    async def asyncSetUp(self) -> None:
        self.client = PetKitClient.__new__(PetKitClient)
        self.cipria = _pet(101401310, "Cipria")
        self.tali = _pet(101401320, "Tali")
        self.tea = _pet(101401316, "Tea")
        self.client.petkit_entities = {
            101401310: self.cipria,
            101401320: self.tali,
            101401316: self.tea,
        }

    async def test_last_meal_is_the_most_recent_for_that_pet(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        # Cipria's later meal wins over her earlier one
        self.assertEqual(self.cipria.last_meal_time, 1753663000)
        self.assertEqual(self.cipria.last_meal_duration, 46)
        self.assertEqual(self.tali.last_meal_time, 1753662700)
        self.assertEqual(self.tali.last_meal_duration, 138)

    async def test_meal_count_ignores_unattributed_visits(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.cipria.meals_today, 2)
        self.assertEqual(self.tali.meals_today, 1)
        # the unrecognised visit is counted against nobody
        self.assertEqual(self.tea.meals_today, 0)

    async def test_pet_that_did_not_eat_reports_zero_not_none(self) -> None:
        """Sensors must exist from the first poll, so stats initialise to zero."""
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.tea.last_meal_time, 0)
        self.assertEqual(self.tea.last_meal_duration, 0)
        self.assertEqual(self.tea.last_feeder_used, "Unknown")

    async def test_feeder_name_is_recorded_for_the_pet_that_ate(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.cipria.last_feeder_used, "Yumshare")

    async def test_string_pet_id_matches_integer_pet_id(self) -> None:
        """RecordsItems.pet_id is a str, Pet.pet_id is an int — the join must survive that."""
        self.assertIsInstance(self.cipria.pet_id, int)
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertNotEqual(self.cipria.last_meal_time, 0)

    async def test_feeder_without_records_is_harmless(self) -> None:
        feeder = _feeder()
        feeder.device_records = None
        await self.client.populate_pet_feeder_stats(feeder)
        self.assertEqual(self.cipria.last_meal_time, 0)


if __name__ == "__main__":
    unittest.main()
