"""Module for handling Bluetooth communication with PetKit devices."""

import asyncio
import base64
from datetime import datetime
from enum import StrEnum
from http import HTTPMethod
import logging
from typing import TYPE_CHECKING
import urllib.parse

from pypetkitapi.command import BLUETOOTH_ACTION
from pypetkitapi.const import (
    BLE_CONNECT_ATTEMPT,
    BLE_END_TRAME,
    BLE_START_TRAME,
    PetkitEndpoint,
)
from pypetkitapi.containers import BleRelay

if TYPE_CHECKING:
    from pypetkitapi import PetKitClient, PypetkitError, WaterFountain

_LOGGER = logging.getLogger(__name__)


class BluetoothManager:
    """Class for handling Bluetooth communication with PetKit devices."""

    def __init__(self, client: "PetKitClient"):
        """Initialize the BluetoothManager class."""
        self.client = client

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

    async def open_ble_connection(self, fountain_id: int) -> bool:
        """Open a BLE connection to the given fountain_id.
        :param fountain_id: The ID of the fountain to open the BLE connection for.
        :return: True if the BLE connection was established, False otherwise.
        """
        _LOGGER.debug("Opening BLE connection to fountain %s", fountain_id)
        water_fountain = await self._get_fountain_instance(fountain_id)
        if water_fountain.is_connected is True:
            _LOGGER.debug("BLE connection already established (id %s)", fountain_id)
            return True
        water_fountain.is_connected = False
        if await self.check_relay_availability(fountain_id) is False:
            _LOGGER.debug("BLE relay not available (id: %s).", fountain_id)
            return False
        response = await self.client.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.BLE_CONNECT,
            data={
                "bleId": fountain_id,
                "type": water_fountain.device_nfo.type,  # type: ignore[union-attr]
                "mac": water_fountain.mac,
            },
            headers=await self.client.get_session_id(),
        )
        if response != {"state": 1}:
            _LOGGER.debug("Unable to open a BLE connection (id %s)", fountain_id)
            return False
        for attempt in range(BLE_CONNECT_ATTEMPT):
            _LOGGER.debug(
                "BLE connection... %s/%s (id %s)",
                attempt,
                BLE_CONNECT_ATTEMPT,
                fountain_id,
            )
            response = await self.client.req.request(
                method=HTTPMethod.POST,
                url=PetkitEndpoint.BLE_POLL,
                data={
                    "bleId": fountain_id,
                    "type": water_fountain.device_nfo.type,  # type: ignore[union-attr]
                    "mac": water_fountain.mac,
                },
                headers=await self.client.get_session_id(),
            )
            if response == 0:
                # Wait for 4 seconds before polling again, connection is still in progress
                await asyncio.sleep(4)
            elif response == -1:
                _LOGGER.debug("Failed to establish BLE connection (id %s)", fountain_id)
                water_fountain.last_ble_poll = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                )
                return False
            elif response == 1:
                _LOGGER.debug(
                    "BLE connection established successfully (id %s)", fountain_id
                )
                water_fountain.is_connected = True
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

        if water_fountain.is_connected is False:
            _LOGGER.debug(
                "BLE connection not established. Cannot close (id %s)", fountain_id
            )
            return

        await self.client.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.BLE_CANCEL,
            data={
                "bleId": fountain_id,
                "type": water_fountain.device_nfo.type,  # type: ignore[union-attr]
                "mac": water_fountain.mac,
            },
            headers=await self.client.get_session_id(),
        )
        _LOGGER.debug("BLE connection closed successfully (id %s)", fountain_id)

    async def build_ble_command(
        self, fountain_id: int, cmd_code: int, cmd_type: int, cmd_data: list[int | str]
    ) -> str:
        """Get the BLE command data for the given fountain_command.
        BLE command format : [header, cmd_code, type_code, counter, length_of_cmd_data, 0, cmd_data + end_bytes]
        :param fountain_id: The ID of the fountain to get the BLE command data for.
        :param cmd_code: BLE command code (1-255).
        :param cmd_type: BLE command type (1 = write, 2 = read).
        :param cmd_data: The BLE command data.
        :return: The BLE command code and the encoded BLE data.
        """
        return await self._encode_ble_data(
            BLE_START_TRAME
            + [
                cmd_code,
                cmd_type,
                await self._get_incremented_ble_counter(fountain_id),
                len(cmd_data),
                0,
            ]
            + cmd_data
            + BLE_END_TRAME
        )

    @staticmethod
    async def _encode_ble_data(byte_list: list) -> str:
        """Encode the given byte_list to a base64 encoded string.
        :param byte_list: The byte list to encode.
        :return: The base64 encoded string.
        """
        byte_array = bytearray(byte_list)
        b64_encoded = base64.b64encode(byte_array)
        return urllib.parse.quote(b64_encoded)

    async def _get_incremented_ble_counter(self, fountain_id: int) -> int:
        """Get the incremented BLE counter for the given fountain_id.
        :param fountain_id: The ID of the fountain to get the incremented BLE counter for.
        :return: The incremented BLE counter.
        """
        water_fountain = await self._get_fountain_instance(fountain_id)
        water_fountain.ble_counter += 1
        if water_fountain.ble_counter > 255:
            water_fountain.ble_counter = 0
        return water_fountain.ble_counter

    async def send_ble_command(
        self, fountain_id: int, action: StrEnum, setting: dict | None = None
    ) -> bool:
        """Send the given BLE command to the fountain_id.
        :param fountain_id: The ID of the fountain to send the command to.
        :param action: The BLE command to send.
        :param setting: The setting to send with the command.
        :return: True if the command was sent successfully, False otherwise.
        """
        if action not in BLUETOOTH_ACTION:
            raise PypetkitError(f"Bluetooth command {action} not supported.")
        action_info = BLUETOOTH_ACTION.get(action)

        _LOGGER.debug("Sending BLE command %s to fountain %s", action, fountain_id)
        water_fountain = await self._get_fountain_instance(fountain_id)

        if water_fountain.is_connected is False:
            # Fountain is not connected, try to establish a connection
            if not await self.open_ble_connection(fountain_id):
                _LOGGER.debug(
                    "BLE connection not established, can't send command (id %s)",
                    fountain_id,
                )
                return False

        if callable(action_info.data):
            cmd_data = action_info.data(setting)
        else:
            cmd_data = action_info.data

        response = await self.client.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.BLE_CONTROL_DEVICE,
            data={
                "bleId": water_fountain.id,
                "cmd": action_info.cmd_code,
                "data": await self.build_ble_command(
                    fountain_id, action_info.cmd_code, action_info.cmd_type, cmd_data
                ),
                "mac": water_fountain.mac,
                "type": water_fountain.device_nfo.type,  # type: ignore[union-attr]
            },
            headers=await self.client.get_session_id(),
        )
        if response != 1:
            _LOGGER.error("Failed to send BLE command (id %s)", fountain_id)
            return False
        _LOGGER.debug("BLE command sent successfully (id %s)", fountain_id)
        return True
