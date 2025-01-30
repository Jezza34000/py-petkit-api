import unittest
from pypetkitapi.schedule_container import Schedule, Owner, Type
from pydantic import ValidationError


fake_schedule_data = {
    "result": {
        "lastKey": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "list": [
            {
                "alarmBefore": 0,
                "createdAt": "2025-01-06T18:54:24.639+0000",
                "deviceId": "400008874",
                "deviceType": "24",
                "id": "68764571b67334c6548418f61fa",
                "name": "Next adding water reminder",
                "owner": {
                    "deviceCount": 0,
                    "id": "100710521",
                    "petCount": 0,
                    "userCount": 0,
                },
                "repeat": "3w",
                "status": 0,
                "time": "2025-02-04T18:54:23.000+0000",
                "type": {
                    "enable": 1,
                    "id": "16",
                    "img": "https://domain.com/img.png",
                    "isCustom": 0,
                    "name": "Next adding water reminder",
                    "priority": 1,
                    "repeatOption": "w,d",
                    "rpt": "",
                    "withDeviceType": "14,24",
                    "withPet": 0,
                },
                "userCustomId": 0,
            },
            {
                "alarmBefore": 0,
                "createdAt": "2025-01-29T11:29:28.392+0000",
                "deviceId": "4000756478",
                "deviceType": "15",
                "id": "998a145214bbec9e00054871719",
                "name": "Add cat litter",
                "owner": {
                    "deviceCount": 0,
                    "id": "999985414",
                    "petCount": 0,
                    "userCount": 0,
                },
                "repeat": "1w",
                "status": 0,
                "time": "2025-02-05T11:30:27.238+0000",
                "type": {
                    "enable": 1,
                    "id": "13",
                    "img": "https://domain.com/img.png",
                    "isCustom": 0,
                    "name": "Add cat litter",
                    "priority": 1,
                    "repeatOption": "d,w",
                    "rpt": "1w",
                    "scheduleAppoint": "1",
                    "withDeviceType": "15",
                    "withPet": 0,
                },
                "userCustomId": 0,
            },
        ],
    }
}


class TestScheduleModel(unittest.TestCase):
    """Test the Schedule model class."""

    def test_schedule_creation(self):
        """Test the creation of Schedule instances from fake data."""
        for schedule_data in fake_schedule_data["result"]["list"]:
            schedule = Schedule(**schedule_data)
            self.assertIsInstance(schedule, Schedule)
            self.assertEqual(schedule.device_id, schedule_data["deviceId"])
            self.assertEqual(schedule.name, schedule_data["name"])

    def test_schedule_owner(self):
        """Test the owner data within the Schedule instances."""
        for schedule_data in fake_schedule_data["result"]["list"]:
            schedule = Schedule(**schedule_data)
            self.assertIsInstance(schedule.owner, Owner)
            self.assertEqual(schedule.owner.id, schedule_data["owner"]["id"])

    def test_schedule_type(self):
        """Test the type data within the Schedule instances."""
        for schedule_data in fake_schedule_data["result"]["list"]:
            schedule = Schedule(**schedule_data)
            self.assertIsInstance(schedule.type, Type)
            self.assertEqual(schedule.type.id, schedule_data["type"]["id"])

    def test_invalid_schedule_data(self):
        """Test the validation error for invalid schedule data."""
        invalid_data = fake_schedule_data["result"]["list"][0].copy()
        invalid_data["alarmBefore"] = "str"  # Invalid data type
        try:
            Schedule(**invalid_data)
        except ValidationError as e:
            self.assertIn("alarmBefore", str(e))
        else:
            self.fail("ValidationError not raised")

    def test_get_endpoint(self):
        """Test the get_endpoint method of the Schedule class."""
        device_type = "any_device_type"
        expected_endpoint = "schedule/schedules"
        self.assertEqual(Schedule.get_endpoint(device_type), expected_endpoint)

    def test_query_param(self):
        """Test the get_endpoint method of the Schedule class."""
        expected_result = {"limit": 20}
        self.assertEqual(Schedule.query_param(None, None), expected_result)


if __name__ == "__main__":
    unittest.main()
