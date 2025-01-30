import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from pypetkitapi.client import PetKitClient
from pypetkitapi.containers import SessionInfo, Device, AccountData, Pet, RegionInfo


class TestPetKitClient(unittest.IsolatedAsyncioTestCase):

    @patch("pypetkitapi.client.PrepReq.request", new_callable=AsyncMock)
    async def test_login(self, mock_request):
        mock_response = {
            "session": {
                "id": "session_id",
                "userId": "user_id",
                "expiresIn": 3600,
                "createdAt": "2023-01-01T00:00:00.000Z",
            }
        }
        mock_request.return_value = mock_response

        await self.client.login()
        self.assertIsNotNone(self.client._session)
        self.assertEqual(self.client._session.id, "session_id")

    @patch("pypetkitapi.client.PrepReq.request", new_callable=AsyncMock)
    async def test_get_account_data(self, mock_request):
        mock_response = {
            "list": [
                {
                    "deviceId": 1,
                    "deviceType": "feeder",
                    "deviceName": "Feeder 1",
                    "createdAt": 1609459200,
                    "groupId": 1,
                    "type": 1,
                    "typeCode": 1,
                    "uniqueId": "unique_id_1",
                }
            ]
        }
        mock_request.return_value = mock_response

        await self.client._get_account_data()
        self.assertEqual(len(self.client.account_data), 1)
        self.assertEqual(len(self.client.petkit_entities), 1)

    @patch("pypetkitapi.client.PrepReq.request", new_callable=AsyncMock)
    async def test_get_devices_data(self, mock_request):
        mock_response = {
            "list": [
                {
                    "deviceId": 1,
                    "deviceType": "feeder",
                    "deviceName": "Feeder 1",
                    "createdAt": 1609459200,
                    "groupId": 1,
                    "type": 1,
                    "typeCode": 1,
                    "uniqueId": "unique_id_1",
                }
            ]
        }
        mock_request.return_value = mock_response

        await self.client.get_devices_data()
        self.assertEqual(len(self.client.petkit_entities), 1)

    @patch("pypetkitapi.client.PrepReq.request", new_callable=AsyncMock)
    async def test_send_api_request(self, mock_request):
        mock_request.return_value = True
        device = Device(
            createdAt=1609459200,
            deviceId=1,
            deviceName="Feeder 1",
            deviceType="feeder",
            groupId=1,
            type=1,
            typeCode=1,
            uniqueId="unique_id_1",
        )
        self.client.petkit_entities[1] = device

        result = await self.client.send_api_request(1, "UPDATE_SETTING")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
