"""Pypetkit Client: A Python library for interfacing with PetKit"""

import asyncio
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
from http import HTTPMethod
import logging
from typing import Any

import aiohttp
from aiohttp import ContentTypeError
import m3u8

from pypetkitapi.bluetooth import BluetoothManager
from pypetkitapi.command import ACTIONS_MAP
from pypetkitapi.const import (
    CLIENT_NFO,
    DEFAULT_COUNTRY,
    DEFAULT_TZ,
    DEVICE_DATA,
    DEVICE_RECORDS,
    DEVICE_STATS,
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    DEVICES_PURIFIER,
    DEVICES_WATER_FOUNTAIN,
    ERR_KEY,
    FEEDER_WITH_CAMERA,
    LITTER_NO_CAMERA,
    LITTER_WITH_CAMERA,
    LOGIN_DATA,
    PET,
    RES_KEY,
    T3,
    T4,
    T5,
    T6,
    Header,
    PetkitDomain,
    PetkitEndpoint,
)
from pypetkitapi.containers import (
    AccountData,
    Device,
    Pet,
    PetDetails,
    RegionInfo,
    SessionInfo,
)
from pypetkitapi.exceptions import (
    PetkitAuthenticationError,
    PetkitAuthenticationUnregisteredEmailError,
    PetkitInvalidHTTPResponseCodeError,
    PetkitInvalidResponseFormat,
    PetkitRegionalServerNotFoundError,
    PetkitSessionError,
    PetkitSessionExpiredError,
    PetkitTimeoutError,
    PypetkitError,
)
from pypetkitapi.feeder_container import Feeder, FeederRecord
from pypetkitapi.litter_container import Litter, LitterRecord, LitterStats, PetOutGraph
from pypetkitapi.purifier_container import Purifier
from pypetkitapi.utils import get_timezone_offset
from pypetkitapi.water_fountain_container import WaterFountain, WaterFountainRecord

data_handlers = {}


def data_handler(data_type):
    """Register a data handler for a specific data type."""

    def wrapper(func):
        data_handlers[data_type] = func
        return func

    return wrapper


_LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """Petkit Client"""

    def __init__(
        self,
        username: str,
        password: str,
        region: str,
        timezone: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the PetKit Client."""

        if region is None or not region.strip():
            region = DEFAULT_COUNTRY
        if timezone is None or not timezone.strip():
            timezone = DEFAULT_TZ

        self.username = username
        self.password = password
        self.region = region.lower()
        self.timezone = timezone
        self._session: SessionInfo | None = None
        self.account_data: list[AccountData] = []
        self.petkit_entities: dict[
            int, Feeder | Litter | WaterFountain | Purifier | Pet
        ] = {}
        self.aiohttp_session = session or aiohttp.ClientSession()
        self.req = PrepReq(
            base_url=PetkitDomain.PASSPORT_PETKIT,
            session=self.aiohttp_session,
            timezone=self.timezone,
        )
        self.bluetooth_manager = BluetoothManager(self)
        from pypetkitapi import MediaManager

        from . import __version__

        self.media_manager = MediaManager()

        _LOGGER.debug("PetKit Client initialized (version %s)", __version__)

    async def _get_base_url(self) -> None:
        """Get the list of API servers, filter by region, and return the matching server."""
        _LOGGER.debug("Getting API server list")
        self.req.base_url = PetkitDomain.PASSPORT_PETKIT

        if self.region.lower() == "china" or self.region.lower() == "cn":
            self.req.base_url = PetkitDomain.CHINA_SRV
            _LOGGER.debug("Using specific China server: %s", PetkitDomain.CHINA_SRV)
            return

        response = await self.req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.REGION_SERVERS,
        )

        # Filter the servers by region
        for region in response.get("list", []):
            server = RegionInfo(**region)
            if server.name.lower() == self.region or server.id.lower() == self.region:
                self.region = server.id.lower()
                self.req.base_url = server.gateway
                _LOGGER.debug("Found matching server: %s", server)
                return
        raise PetkitRegionalServerNotFoundError(self.region)

    async def request_login_code(self) -> bool:
        """Request a login code to be sent to the user's email."""
        _LOGGER.debug("Requesting login code for username: %s", self.username)
        response = await self.req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.GET_LOGIN_CODE,
            params={"username": self.username},
        )
        if response:
            _LOGGER.info("Login code sent to user's email")
            return True
        return False

    async def login(self, valid_code: str | None = None) -> None:
        """Login to the PetKit service and retrieve the appropriate server.
        :param valid_code: The valid code sent to the user's email.
        """
        # Retrieve the list of servers
        self._session = None
        await self._get_base_url()

        _LOGGER.info("Logging in to PetKit server")

        # Prepare the data to send
        client_nfo = CLIENT_NFO.copy()
        client_nfo["timezoneId"] = self.timezone
        client_nfo["timezone"] = get_timezone_offset(self.timezone)

        data = LOGIN_DATA.copy()
        data["client"] = str(client_nfo)
        data["encrypt"] = "1"
        data["region"] = self.region
        data["username"] = self.username

        if valid_code:
            _LOGGER.debug("Login method: using valid code")
            data["validCode"] = valid_code
        else:
            _LOGGER.debug("Login method: using password")
            data["password"] = hashlib.md5(
                self.password.encode()
            ).hexdigest()  # noqa: S324

        # Send the login request
        response = await self.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.LOGIN,
            data=data,
        )
        session_data = response["session"]
        self._session = SessionInfo(**session_data)
        expiration_date = datetime.now() + timedelta(seconds=self._session.expires_in)
        _LOGGER.debug("Login successful (token expiration %s)", expiration_date)

    async def refresh_session(self) -> None:
        """Refresh the session."""
        _LOGGER.debug("Refreshing session")
        response = await self.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.REFRESH_SESSION,
            data=LOGIN_DATA,
            headers=await self.get_session_id(),
        )
        session_data = response["session"]
        self._session = SessionInfo(**session_data)
        self._session.refreshed_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        _LOGGER.debug("Session refreshed at %s", self._session.refreshed_at)

    async def validate_session(self) -> None:
        """Check if the session is still valid and refresh or re-login if necessary."""
        if self._session is None:
            _LOGGER.debug("No token, logging in")
            await self.login()
            return

        created = datetime.strptime(self._session.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        is_expired = datetime.now(tz=created.tzinfo) - created >= timedelta(
            seconds=self._session.expires_in
        )

        if is_expired:
            _LOGGER.debug("Token expired, re-logging in")
            await self.login()
        # elif (max_age / 2) < token_age < max_age:
        #     _LOGGER.debug("Token still OK, but refreshing session")
        #     await self.refresh_session()

    async def get_session_id(self) -> dict:
        """Return the session ID."""
        await self.validate_session()
        if self._session is None:
            raise PetkitSessionError("No session ID available")
        return {"F-Session": self._session.id, "X-Session": self._session.id}

    async def _get_pet_details(self) -> list[PetDetails]:
        """Fetch pet details from the PetKit API."""
        _LOGGER.debug("Fetching user details")
        response = await self.req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.DETAILS,
            headers=await self.get_session_id(),
        )
        user_details = response.get("user", {})
        dogs = user_details.get("dogs", [])
        return [PetDetails(**dog) for dog in dogs]

    async def _get_account_data(self) -> None:
        """Get the account data from the PetKit service."""
        _LOGGER.debug("Fetching account data")
        response = await self.req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.FAMILY_LIST,
            headers=await self.get_session_id(),
        )
        self.account_data = [AccountData(**account) for account in response]

        # Add pets to device_list
        for account in self.account_data:
            if account.pet_list:
                for pet in account.pet_list:
                    self.petkit_entities[pet.pet_id] = pet
                    pet.device_nfo = Device(
                        deviceType=PET,
                        deviceId=pet.pet_id,
                        createdAt=pet.created_at,
                        deviceName=pet.pet_name,
                        groupId=0,
                        type=0,
                        typeCode=0,
                        uniqueId=str(pet.sn),
                    )

        # Fetch pet details and update pet information
        pet_details_list = await self._get_pet_details()
        for pet_details in pet_details_list:
            pet_id = pet_details.id
            if pet_id in self.petkit_entities:
                self.petkit_entities[pet_id].pet_details = pet_details

    async def get_devices_data(self) -> None:
        """Get the devices data from the PetKit servers."""
        start_time = datetime.now()
        if not self.account_data:
            await self._get_account_data()

        device_list = self._collect_devices()
        main_tasks, record_tasks, media_tasks = self._prepare_tasks(device_list)

        await asyncio.gather(*main_tasks)
        await asyncio.gather(*record_tasks)
        await asyncio.gather(*media_tasks)
        await self._execute_stats_tasks()

        end_time = datetime.now()
        _LOGGER.debug("Petkit data fetched successfully in: %s", end_time - start_time)

    def _collect_devices(self) -> list[Device]:
        """Collect all devices from account data.
        :return: List of devices.
        """
        device_list = []
        for account in self.account_data:
            _LOGGER.debug("List devices data for account: %s", account)
            if account.device_list:
                _LOGGER.debug("Devices in account: %s", account.device_list)
                device_list.extend(account.device_list)
                _LOGGER.debug("Found %s devices", len(account.device_list))
        return device_list

    def _prepare_tasks(self, device_list: list[Device]) -> tuple[list, list, list]:
        """Prepare main and record tasks based on device types.
        :param device_list: List of devices.
        :return: Tuple of main tasks, record tasks and media tasks.
        """
        main_tasks: list = []
        record_tasks: list = []
        media_tasks: list = []

        for device in device_list:
            device_type = device.device_type

            if device_type in DEVICES_FEEDER:
                main_tasks.append(self._fetch_device_data(device, Feeder))
                record_tasks.append(self._fetch_device_data(device, FeederRecord))
                self._add_feeder_task_by_type(media_tasks, device_type, device)

            elif device_type in DEVICES_LITTER_BOX:
                main_tasks.append(self._fetch_device_data(device, Litter))
                record_tasks.append(self._fetch_device_data(device, LitterRecord))
                self._add_lb_task_by_type(
                    record_tasks, media_tasks, device_type, device
                )

            elif device_type in DEVICES_WATER_FOUNTAIN:
                main_tasks.append(self._fetch_device_data(device, WaterFountain))
                record_tasks.append(
                    self._fetch_device_data(device, WaterFountainRecord)
                )

            elif device_type in DEVICES_PURIFIER:
                main_tasks.append(self._fetch_device_data(device, Purifier))

        return main_tasks, record_tasks, media_tasks

    def _add_lb_task_by_type(
        self, record_tasks: list, media_tasks: list, device_type: str, device: Device
    ) -> None:
        """Add specific tasks for litter box devices.
        :param record_tasks: List of record tasks.
        :param media_tasks: List of media tasks.
        :param device_type: Device type.
        :param device: Device data.
        """
        if device_type in LITTER_NO_CAMERA:
            record_tasks.append(self._fetch_device_data(device, LitterStats))
        if device_type in LITTER_WITH_CAMERA:
            record_tasks.append(self._fetch_device_data(device, PetOutGraph))
            media_tasks.append(self._fetch_media(device))

    def _add_feeder_task_by_type(
        self, media_tasks: list, device_type: str, device: Device
    ) -> None:
        """Add specific tasks for feeder box devices.
        :param media_tasks: List of media tasks.
        :param device_type: Device type.
        :param device: Device data.
        """
        if device_type in FEEDER_WITH_CAMERA:
            media_tasks.append(self._fetch_media(device))

    async def _execute_stats_tasks(self) -> None:
        """Execute tasks to populate pet stats."""
        stats_tasks = [
            self.populate_pet_stats(entity)
            for device_id, entity in self.petkit_entities.items()
            if isinstance(entity, Litter)
        ]
        await asyncio.gather(*stats_tasks)

    async def _fetch_media(self, device: Device) -> None:
        """Fetch media data from the PetKit servers.
        :param device: Device data.
        """
        _LOGGER.debug("Fetching media data for device: %s", device.device_id)

        device_entity = self.petkit_entities[device.device_id]
        device_entity.medias = await self.media_manager.gather_all_media_from_cloud(
            [device_entity]
        )

    async def _fetch_device_data(
        self,
        device: Device,
        data_class: type[
            Feeder
            | Litter
            | WaterFountain
            | Purifier
            | FeederRecord
            | LitterRecord
            | WaterFountainRecord
            | PetOutGraph
            | LitterStats
        ],
    ) -> None:
        """Fetch the device data from the PetKit servers.
        :param device: Device data.
        :param data_class: Data class
        """
        device_type = device.device_type

        _LOGGER.debug("Reading device type : %s (id=%s)", device_type, device.device_id)

        endpoint = data_class.get_endpoint(device_type)

        if endpoint is None:
            _LOGGER.debug("Endpoint not found for device type: %s", device_type)
            return

        # Specific device ask for data from the device
        device_cont = None
        if self.petkit_entities.get(device.device_id, None):
            device_cont = self.petkit_entities[device.device_id]

        query_param = data_class.query_param(device, device_cont)

        response = await self.req.request(
            method=HTTPMethod.POST,
            url=f"{device_type}/{endpoint}",
            params=query_param,
            headers=await self.get_session_id(),
        )

        # Workaround for the litter box T6
        if isinstance(response, dict) and response.get("list", None):
            response = response.get("list", [])

        # Check if the response is a list or a dict
        if isinstance(response, list):
            device_data = [data_class(**item) for item in response]
        elif isinstance(response, dict):
            device_data = data_class(**response)
        else:
            _LOGGER.error("Unexpected response type: %s", type(response))
            return

        # Dispatch to the appropriate data handler
        handler = data_handlers.get(data_class.data_type)
        if handler:
            await handler(self, device, device_data, device_type)
        else:
            _LOGGER.error("Unknown data type: %s", data_class.data_type)

    @data_handler(DEVICE_DATA)
    async def _handle_device_data(
        self,
        device: Device,
        device_data: Feeder | Litter | WaterFountain | Purifier,
        device_type: str,
    ):
        """Handle device data."""
        self.petkit_entities[device.device_id] = device_data
        self.petkit_entities[device.device_id].device_nfo = device
        _LOGGER.debug("Device data fetched OK for %s", device_type)

    @data_handler(DEVICE_RECORDS)
    async def _handle_device_records(
        self, device: Device, device_data, device_type: str
    ):
        """Handle device records."""
        entity = self.petkit_entities.get(device.device_id)
        if entity and isinstance(entity, (Feeder, Litter, WaterFountain)):
            entity.device_records = device_data
            _LOGGER.debug("Device records fetched OK for %s", device_type)
        else:
            _LOGGER.warning(
                "Cannot assign device_records to entity of type %s",
                type(entity),
            )

    @data_handler(DEVICE_STATS)
    async def _handle_device_stats(self, device: Device, device_data, device_type: str):
        """Handle device stats."""
        entity = self.petkit_entities.get(device.device_id)
        if isinstance(entity, Litter):
            if device_type in LITTER_NO_CAMERA:
                entity.device_stats = device_data
            if device_type in LITTER_WITH_CAMERA:
                entity.device_pet_graph_out = device_data
            _LOGGER.debug("Device stats fetched OK for %s", device_type)
        else:
            _LOGGER.warning(
                "Cannot assign device_stats or device_pet_graph_out to entity of type %s",
                type(entity),
            )

    async def get_pets_list(self) -> list[Pet]:
        """Extract and return the list of pets.
        :return: List of pets.
        """
        return [
            entity
            for entity in self.petkit_entities.values()
            if isinstance(entity, Pet)
        ]

    @staticmethod
    def get_safe_value(value: int | None, default: int = 0) -> int:
        """Return the value if not None, otherwise return the default.
        :param value: Value to check.
        :param default: Default value.
        :return: Value or default.
        """
        return value if value is not None else default

    @staticmethod
    def calculate_duration(start: int | None, end: int | None) -> int:
        """Calculate the duration, ensuring both start and end are not None.
        :param start: Start time.
        :param end: End time.
        :return: Duration.
        """
        if start is None or end is None:
            return 0
        return end - start

    async def populate_pet_stats(self, stats_data: Litter) -> None:
        """Collect data from litter data to populate pet stats.
        :param stats_data: Litter data.
        """
        if not stats_data.device_nfo:
            _LOGGER.warning(
                "No device info for %s can't populate pet infos", stats_data
            )
            return

        pets_list = await self.get_pets_list()
        for pet in pets_list:
            if stats_data.device_nfo.device_type in [T3, T4]:
                await self.init_pet_stats(pet)
                await self._process_litter_no_camera(pet, stats_data)
            elif stats_data.device_nfo.device_type in [T5, T6]:
                await self.init_pet_stats(pet)
                await self._process_litter_camera(pet, stats_data)

    @staticmethod
    async def init_pet_stats(pet: Pet) -> None:
        """Initialize pet stats.
        Allow pet stats to be displayed in HA even if no data is available.
        :param pet: Pet data.
        """
        pet.last_litter_usage = 0
        pet.last_device_used = "Unknown"
        pet.last_duration_usage = 0
        pet.last_measured_weight = 0

    async def _process_litter_no_camera(self, pet: Pet, device_records: Litter) -> None:
        """Process litter T3/T4 records (litter without camera).
        :param pet: Pet data.
        :param device_records: Litter data.
        """
        for stat in (
            s
            for s in device_records.device_records or []
            if isinstance(s, LitterRecord)
        ):
            if stat.pet_id == pet.pet_id and (
                pet.last_litter_usage is None
                or self.get_safe_value(stat.timestamp) > pet.last_litter_usage
            ):
                pet.last_litter_usage = (
                    stat.timestamp if stat.timestamp is not None else 0
                )
                pet.last_measured_weight = self.get_safe_value(
                    stat.content.pet_weight if stat.content else None
                )
                pet.last_duration_usage = self.calculate_duration(
                    stat.content.time_in if stat.content else None,
                    stat.content.time_out if stat.content else None,
                )
                pet.last_device_used = getattr(
                    device_records.device_nfo, "device_name", "Unknown"
                ).capitalize()

    async def _process_litter_camera(self, pet: Pet, pet_graphs: Litter) -> None:
        """Process litter T5/T6 records (litter WITH camera).
        :param pet: Pet data.
        :param pet_graphs: Litter data.
        """
        for graph in pet_graphs.device_pet_graph_out or []:
            if graph.pet_id == pet.pet_id and (
                pet.last_litter_usage is None
                or self.get_safe_value(graph.time) > pet.last_litter_usage
            ):
                pet.last_litter_usage = graph.time or 0
                pet.last_measured_weight = self.get_safe_value(
                    graph.content.pet_weight if graph.content else None
                )
                pet.last_duration_usage = self.get_safe_value(graph.toilet_time) or 0
                pet.last_device_used = getattr(
                    pet_graphs.device_nfo, "device_name", "Unknown"
                ).capitalize()

    async def get_cloud_video(self, video_url: str) -> dict[str, str | int] | None:
        """Get the video m3u8 link from the cloud.
        :param video_url: URL of the video.
        :return: Video data.
        """
        response = await self.req.request(
            method=HTTPMethod.POST,
            url=video_url,
            headers=await self.get_session_id(),
        )
        if not isinstance(response, list) or not response:
            _LOGGER.warning(
                "No video data found from cloud, looks like you don't have a care+ subscription ? or video is not uploaded yet."
            )
            return None
        return response[0]

    async def extract_segments_m3u8(
        self, m3u8_url: str
    ) -> tuple[Any, str | None, list[str | None]]:
        """Extract segments from the m3u8 file.
        :param: m3u8_url: URL of the m3u8 file
        :return: aes_key, key_iv, segment_lst
        """
        # Extract segments from m3u8 file
        response = await self.req.request(
            method=HTTPMethod.GET,
            url=m3u8_url,
            headers=await self.get_session_id(),
        )
        m3u8_obj = m3u8.loads(response[RES_KEY])

        if not m3u8_obj.segments or not m3u8_obj.keys:
            return None, None, []

        # Extract segments from m3u8 file
        segment_lst = [segment.uri for segment in m3u8_obj.segments]
        # Extract key_uri and key_iv from m3u8 file
        key_uri = m3u8_obj.keys[0].uri
        key_iv = str(m3u8_obj.keys[0].iv)

        if not key_uri or not key_iv:
            return None, None, []

        # Extract aes_key from video segments
        response = await self.req.request(
            method=HTTPMethod.GET,
            url=key_uri,
            full_url=True,
            headers=await self.get_session_id(),
        )
        return response[RES_KEY], key_iv, segment_lst

    async def send_api_request(
        self,
        device_id: int,
        action: StrEnum,
        setting: dict | None = None,
    ) -> bool:
        """Control the device using the PetKit API.
        :param device_id: ID of the device.
        :param action: Action to perform.
        :param setting: Setting to apply.
        :return: True if the command was successful, False otherwise.
        """
        device = self.petkit_entities.get(device_id, None)
        if not device:
            raise PypetkitError(f"Device with ID {device_id} not found.")
        if device.device_nfo is None:
            raise PypetkitError(f"Device with ID {device_id} has no device_nfo.")

        _LOGGER.debug(
            "Control API device=%s id=%s action=%s param=%s",
            device.device_nfo.device_type,
            device_id,
            action,
            setting,
        )

        # Check if the device type is supported
        if device.device_nfo.device_type:
            device_type = device.device_nfo.device_type
        else:
            raise PypetkitError(
                "Device type is not available, and is mandatory for sending commands."
            )
        # Check if the action is supported
        if action not in ACTIONS_MAP:
            raise PypetkitError(f"Action {action} not supported.")

        action_info = ACTIONS_MAP[action]
        _LOGGER.debug(action)
        _LOGGER.debug(action_info)
        if device_type not in action_info.supported_device:
            _LOGGER.error(
                "Device type %s not supported for action %s.", device_type, action
            )
            return False

        # Get the endpoint
        if callable(action_info.endpoint):
            endpoint = action_info.endpoint(device)
            _LOGGER.debug("Endpoint from callable")
        else:
            endpoint = action_info.endpoint
            _LOGGER.debug("Endpoint field")
        url = f"{device.device_nfo.device_type}/{endpoint}"

        # Get the parameters
        if setting is not None:
            params = action_info.params(device, setting)
        else:
            params = action_info.params(device)

        res = await self.req.request(
            method=HTTPMethod.POST,
            url=url,
            data=params,
            headers=await self.get_session_id(),
        )
        _LOGGER.debug("Command execution success, API response : %s", res)
        return True

    async def close(self) -> None:
        """Close the aiohttp session if it was created by the client."""
        if self.aiohttp_session:
            await self.aiohttp_session.close()


class PrepReq:
    """Prepare the request to the PetKit API."""

    def __init__(
        self, base_url: str, session: aiohttp.ClientSession, timezone: str
    ) -> None:
        """Initialize the request."""
        self.base_url = base_url
        self.session = session
        self.timezone = timezone
        self.base_headers = self._generate_header()

    def _generate_header(self) -> dict[str, str]:
        """Create header for interaction with API endpoint."""
        return {
            "Accept": Header.ACCEPT.value,
            "Accept-Language": Header.ACCEPT_LANG.value,
            "Accept-Encoding": Header.ENCODING.value,
            "Content-Type": Header.CONTENT_TYPE.value,
            "User-Agent": Header.AGENT.value,
            "X-Img-Version": Header.IMG_VERSION.value,
            "X-Locale": Header.LOCALE.value,
            "X-Client": Header.CLIENT.value,
            "X-Hour": Header.HOUR.value,
            "X-TimezoneId": self.timezone,
            "X-Api-Version": Header.API_VERSION.value,
            "X-Timezone": get_timezone_offset(self.timezone),
        }

    async def request(
        self,
        method: str,
        url: str,
        full_url: bool = False,
        params=None,
        data=None,
        headers=None,
    ) -> dict:
        """Make a request to the PetKit API.
        :param method: HTTP method.
        :param url: URL of the API endpoint.
        :param full_url: Use full URL.
        :param params: Parameters to send.
        :param data: Data to send.
        :param headers: Headers to send.
        :return: Response from the API.
        """
        _url = url if full_url else "/".join(s.strip("/") for s in [self.base_url, url])
        _headers = {**self.base_headers, **(headers or {})}
        _LOGGER.debug("Request: %s %s", method, _url)
        try:
            async with self.session.request(
                method,
                _url,
                params=params,
                data=data,
                headers=_headers,
            ) as resp:
                return await self._handle_response(resp, _url)
        except aiohttp.ClientConnectorError as e:
            raise PetkitTimeoutError(f"Cannot connect to host: {e}") from e

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse, url: str) -> dict:
        """Handle the response from the PetKit API.
        :param response: Response from the API.
        :param url: URL of the API endpoint.
        :return: Data from the API.
        """
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise PetkitInvalidHTTPResponseCodeError(
                f"Request failed with status code {e.status}"
            ) from e

        try:
            if response.content_type == "application/json":
                response_json = await response.json()
            else:
                return {RES_KEY: await response.text()}
        except ContentTypeError:
            raise PetkitInvalidResponseFormat(
                "Response is not in JSON format"
            ) from None
        # Check for errors in the response
        if ERR_KEY in response_json:
            error_code = int(response_json[ERR_KEY].get("code", 0))
            error_msg = response_json[ERR_KEY].get("msg", "Unknown error")

            match error_code:
                case 5:
                    raise PetkitSessionExpiredError(f"Session expired: {error_msg}")
                case 122:
                    raise PetkitAuthenticationError(
                        f"Authentication failed: {error_msg}"
                    )
                case 125:
                    raise PetkitAuthenticationUnregisteredEmailError
                case _:
                    raise PypetkitError(
                        f"Request failed code : {error_code}, details : {error_msg} url : {url}"
                    )

        # Check for success in the response
        if RES_KEY in response_json:
            return response_json[RES_KEY]

        raise PypetkitError("Unexpected response format")
