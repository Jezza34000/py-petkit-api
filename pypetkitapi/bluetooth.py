"""Module for handling Bluetooth communication with PetKit devices."""

import asyncio
import base64
from datetime import datetime
from http import HTTPMethod
import logging
from typing import TYPE_CHECKING
import urllib.parse

from pypetkitapi.command import FOUNTAIN_COMMAND, FountainAction
from pypetkitapi.const import (
    BLE_CONNECT_ATTEMPT,
    BLE_END_TRAME,
    BLE_START_TRAME,
    PTK_DBG,
    BluetoothState,
    PetkitEndpoint,
)
from pypetkitapi.containers import BleRelay

if TYPE_CHECKING:
    from pypetkitapi import PetKitClient, WaterFountain

_LOGGER = logging.getLogger(__name__)


class BluetoothManager:
    """Class for handling Bluetooth communication with PetKit devices."""

    def __init__(self, client: "PetKitClient", **kwargs):
        """Initialize the BluetoothManager class."""
        self.client = client
        self._debug_test = kwargs.get(PTK_DBG, False)

    async def _get_fountain_instance(self, fountain_id: int) -> "WaterFountain":
        """Get the WaterFountain instance for the given fountain_id.
        :param fountain_id: The ID of the fountain to get the instance for.
        :return: The WaterFountain instance for the given fountain_id.
        """
        from pypetkitapi.water_fountain_container import WaterFountain

        water_fountain = self.client.petkit_entities.get(fountain_id)
        if not isinstance(water_fountain, WaterFountain):
            _LOGGER.error("Water fountain with ID %s not found.", fountain_id)
            raise TypeError(f"Water fountain with ID {fountain_id} not found.")
        if water_fountain.device_nfo is None:
            raise ValueError(f"Device info not found for fountain {fountain_id}")

        return water_fountain

    async def check_relay_availability(self, fountain_id: int) -> bool:
        """Check if BLE relay is available for the given fountain_id.
        :param fountain_id: The ID of the fountain to check the relay for.
        :return: True if the relay is available, False otherwise.
        """
        fountain = None
        for account in self.client.account_data:
            if account.device_list:
                fountain = next(
                    (
                        device
                        for device in account.device_list
                        if device.device_id == fountain_id
                    ),
                    None,
                )
                if fountain:
                    break
        if not fountain:
            raise ValueError(
                f"Fountain with device_id {fountain_id} not found for the current account"
            )
        group_id = fountain.group_id
        response = await self.client.req.request(
            method=HTTPMethod.POST,
            url=f"{PetkitEndpoint.BLE_AS_RELAY}",
            params={"groupId": group_id},
            headers=await self.client.get_session_id(),
        )
        ble_relays = [BleRelay(**relay) for relay in response]
        if len(ble_relays) == 0:
            _LOGGER.warning("No BLE relay devices found.")
            return False
        return True

    async def _request_ble_api(
        self,
        endpoint: PetkitEndpoint,
        fountain: "WaterFountain",
        extra_data: dict | None = None,
    ):
        """API Bluetooth request method"""
        data = {
            "bleId": fountain.id,
            "type": fountain.device_nfo.type,  # type: ignore[union-attr]
            "mac": fountain.mac,
        }
        if extra_data:
            data.update(extra_data)

        return await self.client.req.request(
            method=HTTPMethod.POST,
            url=endpoint,
            data=data,
            headers=await self.client.get_session_id(),
        )

    async def open_ble_connection(self, fountain_id: int) -> bool:
        """Open a BLE connection to the given fountain_id.
        :param fountain_id: The ID of the fountain to open the BLE connection for.
        :return: True if the BLE connection was established, False otherwise.
        """
        _LOGGER.debug("Opening BLE connection to fountain %s", fountain_id)
        water_fountain = await self._get_fountain_instance(fountain_id)
        if water_fountain.ble_connection_state == BluetoothState.CONNECTED:
            _LOGGER.debug("BLE connection already established (id %s)", fountain_id)
            return True

        if water_fountain.ble_connection_state == BluetoothState.CONNECTING:
            _LOGGER.debug("BLE connection already in progress (id %s).", fountain_id)
        else:
            if not await self.check_relay_availability(fountain_id):
                _LOGGER.debug("BLE relay not available (id: %s).", fountain_id)
                water_fountain.ble_connection_state = BluetoothState.NOT_CONNECTED
                return False

            response = await self._request_ble_api(
                PetkitEndpoint.BLE_CONNECT, water_fountain
            )
            if response != {"state": 1}:
                _LOGGER.debug("Unable to open a BLE connection (id %s)", fountain_id)
                water_fountain.ble_connection_state = BluetoothState.NOT_CONNECTED
                return False

            water_fountain.ble_connection_state = BluetoothState.CONNECTING

        for attempt in range(BLE_CONNECT_ATTEMPT):
            _LOGGER.debug(
                "BLE connection... attempt: %s (id %s)",
                attempt,
                fountain_id,
            )
            response = await self._request_ble_api(
                PetkitEndpoint.BLE_POLL, water_fountain
            )
            if response == BluetoothState.CONNECTING:
                # Wait for 4 seconds before polling again, connection is still in progress
                await asyncio.sleep(4)
            elif response == BluetoothState.ERROR:
                _LOGGER.debug("Failed to establish BLE connection (id %s)", fountain_id)
                water_fountain.last_ble_poll = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                )
                return False
            elif response == BluetoothState.CONNECTED:
                _LOGGER.debug(
                    "BLE connection established successfully (id %s)", fountain_id
                )
                water_fountain.ble_connection_state = BluetoothState.CONNECTED
                water_fountain.last_ble_poll = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                )
                return True
        _LOGGER.debug(
            "Failed to establish BLE connection reached the max %s attempts allowed (id %s)",
            BLE_CONNECT_ATTEMPT,
            fountain_id,
        )
        return False

    async def close_ble_connection(self, fountain_id: int) -> None:
        """Close the BLE connection to the given fountain_id.
        :param fountain_id: The ID of the fountain to close the BLE connection for.
        :return: None
        """
        _LOGGER.debug("Closing BLE connection to fountain %s", fountain_id)
        water_fountain = await self._get_fountain_instance(fountain_id)

        if water_fountain.ble_connection_state != BluetoothState.CONNECTED:
            _LOGGER.debug(
                "BLE connection not established. Cannot close (id %s) State is=%s",
                fountain_id,
                water_fountain.ble_connection_state,
            )
            return

        await self._request_ble_api(PetkitEndpoint.BLE_CANCEL, water_fountain)
        water_fountain.ble_connection_state = BluetoothState.NOT_CONNECTED
        _LOGGER.debug("BLE connection closed successfully (id %s)", fountain_id)

    async def get_ble_cmd_data(
        self, fountain_command: list, counter: int
    ) -> tuple[int, str]:
        """Get the BLE command data for the given fountain_command.
        :param fountain_command: The fountain command to get the BLE data for.
        :param counter: The BLE counter for the fountain.
        :return: The BLE command code and the encoded BLE data.
        """
        cmd_code = fountain_command[0]
        modified_command = [*fountain_command[:2], counter, *fountain_command[2:]]
        ble_data = [*BLE_START_TRAME, *modified_command, *BLE_END_TRAME]
        encoded_data = await self._encode_ble_data(ble_data)
        return cmd_code, encoded_data

    @staticmethod
    async def _encode_ble_data(byte_list: list) -> str:
        """Encode the given byte_list to a base64 encoded string.
        :param byte_list: The byte list to encode.
        :return: The base64 encoded string.
        """
        byte_array = bytearray(byte_list)
        b64_encoded = base64.b64encode(byte_array)
        return urllib.parse.quote(b64_encoded)

    async def send_ble_command(self, fountain_id: int, command: FountainAction) -> bool:
        """Send the given BLE command to the fountain_id.
        :param fountain_id: The ID of the fountain to send the command to.
        :param command: The command to send to the fountain.
        :return: True if the command was sent successfully, False otherwise.
        """
        _LOGGER.debug("Sending BLE command to fountain %s", fountain_id)
        water_fountain = await self._get_fountain_instance(fountain_id)

        if not await self.open_ble_connection(fountain_id):
            _LOGGER.error(
                "Unable to send BLE command because the connection can't be established (id %s)",
                fountain_id,
            )
            return False

        command_data = FOUNTAIN_COMMAND.get(command)
        if command_data is None:
            _LOGGER.error(
                "BLE fountain command '%s' not found (id %s)", command, fountain_id
            )
            return False
        cmd_code, cmd_data = await self.get_ble_cmd_data(
            list(command_data), water_fountain.ble_counter
        )
        response = await self._request_ble_api(
            PetkitEndpoint.BLE_CONTROL_DEVICE,
            water_fountain,
            extra_data={"cmd": cmd_code, "data": cmd_data},
        )
        if response != 1:
            _LOGGER.error("Failed to send BLE command (id %s)", fountain_id)
            return False
        _LOGGER.debug("BLE command sent successfully (id %s)", fountain_id)
        return True
