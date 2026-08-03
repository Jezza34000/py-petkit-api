"""Per-pet meal attribution from feeder records.

The payload shape below is a trimmed copy of a real `getDeviceRecord` response for
a D4SH with pet recognition: `eat[].items[]` carries `petId` for every meal the AI
managed to attribute, and leaves it out for the ones it did not.
"""

import unittest

from pypetkitapi.client import PetKitClient
from pypetkitapi.containers import Device, Pet
from pypetkitapi.feeder_container import Feeder, FeederRecord, SettingsFeeder

# Pet A ate twice, Pet B once, and one visit went unrecognised.
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
    feeder.settings = SettingsFeeder(eatDetection=1)
    feeder.device_nfo = Device(
        createdAt=1719234118,
        deviceId=300035322,
        deviceName="yumshare",
        deviceType="d4sh",
        groupId=1,
        # real values from a live D4SH-2: type 25, typeCode 2. The guard keys on
        # typeCode, so a fixture that omits it silently fails every test.
        type=25,
        typeCode=2,
        uniqueId="u0001",
    )
    feeder.device_records = FeederRecord(**FAKE_EAT_RECORD)
    return feeder


class TestPetFeederStats(unittest.IsolatedAsyncioTestCase):
    """Per-pet feeder stats derived from eat records."""

    async def asyncSetUp(self) -> None:
        self.client = PetKitClient.__new__(PetKitClient)
        self.pet_a = _pet(101401310, "Pet A")
        self.pet_b = _pet(101401320, "Pet B")
        self.pet_c = _pet(101401316, "Pet C")
        self.client.petkit_entities = {
            101401310: self.pet_a,
            101401320: self.pet_b,
            101401316: self.pet_c,
        }

    async def test_last_meal_is_the_most_recent_for_that_pet(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        # the later meal wins over the earlier one for the same pet
        self.assertEqual(self.pet_a.last_meal_time, 1753663000)
        self.assertEqual(self.pet_a.last_meal_duration, 46)
        self.assertEqual(self.pet_b.last_meal_time, 1753662700)
        self.assertEqual(self.pet_b.last_meal_duration, 138)

    async def test_meal_count_ignores_unattributed_visits(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.pet_a.meals_today, 2)
        self.assertEqual(self.pet_b.meals_today, 1)
        # the unrecognised visit is counted against nobody
        self.assertEqual(self.pet_c.meals_today, 0)

    async def test_pet_that_did_not_eat_reports_zero_not_none(self) -> None:
        """Sensors must exist from the first poll, so stats initialise to zero."""
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.pet_c.last_meal_time, 0)
        self.assertEqual(self.pet_c.last_meal_duration, 0)
        self.assertEqual(self.pet_c.last_feeder_used, "Unknown")

    async def test_feeder_name_is_recorded_for_the_pet_that_ate(self) -> None:
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertEqual(self.pet_a.last_feeder_used, "Yumshare")

    async def test_string_pet_id_matches_integer_pet_id(self) -> None:
        """RecordsItems.pet_id is a str, Pet.pet_id is an int — the join must survive that."""
        self.assertIsInstance(self.pet_a.pet_id, int)
        await self.client.populate_pet_feeder_stats(_feeder())
        self.assertNotEqual(self.pet_a.last_meal_time, 0)

    async def test_feeder_without_records_is_harmless(self) -> None:
        feeder = _feeder()
        feeder.device_records = None
        await self.client.populate_pet_feeder_stats(feeder)
        self.assertEqual(self.pet_a.last_meal_time, 0)


if __name__ == "__main__":
    unittest.main()


class TestPetRecognitionGuard(unittest.IsolatedAsyncioTestCase):
    """The guard must key on CAPABILITY, not on whether a pet has eaten yet."""

    async def asyncSetUp(self) -> None:
        self.client = PetKitClient.__new__(PetKitClient)
        self.pet_a = _pet(101401310, "Pet A")
        self.client.petkit_entities = {101401310: self.pet_a}

    async def test_ai_feeder_initialised_before_first_attributed_meal(self) -> None:
        """Just after the daily reset the AI feeder still reports 0, not None.

        device_records.eat resets at local midnight, so between then and the
        first RECOGNISED meal there is nothing attributed to find. A data-based
        guard blanks the sensors for that whole window.
        """
        feeder = _feeder()
        feeder.device_records = None
        await self.client.populate_pet_feeder_stats(feeder)
        self.assertEqual(self.pet_a.meals_today, 0)
        self.assertEqual(self.pet_a.last_meal_time, 0)

    async def test_ai_feeder_with_only_unrecognised_meals(self) -> None:
        """Meals happened but the AI named nobody: still initialised, count 0."""
        feeder = _feeder()
        feeder.device_records = FeederRecord(
            **{
                "eat": [
                    {
                        "deviceId": 300035322,
                        "items": [
                            {
                                "eatStartTime": 1753662133,
                                "eatEndTime": 1753662301,
                                "duration": 4,
                            }
                        ],
                    }
                ]
            }
        )
        await self.client.populate_pet_feeder_stats(feeder)
        self.assertEqual(self.pet_a.meals_today, 0)


class TestNonAiFeederGuard(unittest.IsolatedAsyncioTestCase):
    """typeCode separates the recognising hardware from the rest."""

    async def asyncSetUp(self) -> None:
        self.client = PetKitClient.__new__(PetKitClient)
        self.pet_a = _pet(101401310, "Pet A")
        self.client.petkit_entities = {101401310: self.pet_a}

    async def test_camera_feeder_without_recognition_gets_no_stats(self) -> None:
        feeder = _feeder()
        feeder.device_nfo.type_code = 1
        await self.client.populate_pet_feeder_stats(feeder)
        self.assertIsNone(self.pet_a.meals_today)
        self.assertIsNone(self.pet_a.last_meal_time)
