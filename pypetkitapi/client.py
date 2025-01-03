"""Pypetkit Client: A Python library for interfacing with PetKit"""

import asyncio
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
from http import HTTPMethod
import logging

import aiohttp
from aiohttp import ContentTypeError

from pypetkitapi.command import ACTIONS_MAP
from pypetkitapi.const import (
    DEVICE_DATA,
    DEVICE_RECORDS,
    DEVICE_STATS,
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    DEVICES_PURIFIER,
    DEVICES_WATER_FOUNTAIN,
    ERR_KEY,
    LOGIN_DATA,
    RES_KEY,
    T4,
    T6,
    Header,
    PetkitDomain,
    PetkitEndpoint,
)
from pypetkitapi.containers import AccountData, Device, Pet, RegionInfo, SessionInfo
from pypetkitapi.exceptions import (
    PetkitAuthenticationError,
    PetkitAuthenticationUnregisteredEmailError,
    PetkitInvalidHTTPResponseCodeError,
    PetkitInvalidResponseFormat,
    PetkitRegionalServerNotFoundError,
    PetkitSessionExpiredError,
    PetkitTimeoutError,
    PypetkitError,
)
from pypetkitapi.feeder_container import Feeder, FeederRecord
from pypetkitapi.litter_container import Litter, LitterRecord, LitterStats, PetOutGraph
from pypetkitapi.purifier_container import Purifier
from pypetkitapi.water_fountain_container import WaterFountain, WaterFountainRecord

_LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """Petkit Client"""

    _session: SessionInfo | None = None
    account_data: list[AccountData] = []
    petkit_entities: dict[int, Feeder | Litter | WaterFountain | Purifier | Pet] = {}

    def __init__(
        self,
        username: str,
        password: str,
        region: str,
        timezone: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the PetKit Client."""
        self.username = username
        self.password = password
        self.region = region.lower()
        self.timezone = timezone
        self._session = None
        self.petkit_entities = {}
        self.aiohttp_session = session or aiohttp.ClientSession()
        self.req = PrepReq(
            base_url=PetkitDomain.PASSPORT_PETKIT, session=self.aiohttp_session
        )

    async def _get_base_url(self) -> None:
        """Get the list of API servers, filter by region, and return the matching server."""
        _LOGGER.debug("Getting API server list")
        self.req.base_url = PetkitDomain.PASSPORT_PETKIT

        if self.region.lower() == "china":
            self.req.base_url = PetkitDomain.CHINA_SRV
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
        """Login to the PetKit service and retrieve the appropriate server."""
        # Retrieve the list of servers
        await self._get_base_url()

        _LOGGER.info("Logging in to PetKit server")

        # Prepare the data to send
        data = LOGIN_DATA.copy()
        data["encrypt"] = "1"
        data["region"] = self.region
        data["username"] = self.username

        if valid_code:
            _LOGGER.debug("Login method: using valid code")
            data["validCode"] = valid_code
        else:
            _LOGGER.debug("Login method: using password")
            pwd = hashlib.md5(self.password.encode()).hexdigest()  # noqa: S324
            data["password"] = pwd  # noqa: S324

        # Send the login request
        response = await self.req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.LOGIN,
            data=data,
        )
        session_data = response["session"]
        self._session = SessionInfo(**session_data)

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
        self._session.created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")

    async def validate_session(self) -> None:
        """Check if the session is still valid and refresh or re-login if necessary."""
        if self._session is None:
            _LOGGER.debug("No token, logging in")
            await self.login()
            return

        created_at = datetime.strptime(
            self._session.created_at,
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )
        current_time = datetime.now(tz=created_at.tzinfo)
        token_age = current_time - created_at
        max_age = timedelta(seconds=self._session.expires_in)
        half_max_age = max_age / 2

        if token_age > max_age:
            _LOGGER.debug("Token expired, re-logging in")
            await self.login()
        elif half_max_age < token_age <= max_age:
            _LOGGER.debug("Token still OK, but refreshing session")
            await self.refresh_session()

    async def get_session_id(self) -> dict:
        """Return the session ID."""
        if self._session is None:
            raise PypetkitError("Session is not initialized.")
        return {"F-Session": self._session.id, "X-Session": self._session.id}

    async def _get_account_data(self) -> None:
        """Get the account data from the PetKit service."""
        await self.validate_session()
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

    async def get_devices_data(self) -> None:
        """Get the devices data from the PetKit servers."""
        await self.validate_session()

        start_time = datetime.now()
        if not self.account_data:
            await self._get_account_data()

        main_tasks = []
        record_tasks = []
        device_list: list[Device] = []

        for account in self.account_data:
            _LOGGER.debug("List devices data for account: %s", account)
            if account.device_list:
                _LOGGER.debug("Devices in account: %s", account.device_list)
                device_list.extend(account.device_list)
                _LOGGER.debug("Found %s devices", len(account.device_list))

        for device in device_list:
            device_type = device.device_type.lower()
            if device_type in DEVICES_FEEDER:
                main_tasks.append(self._fetch_device_data(device, Feeder))
                record_tasks.append(self._fetch_device_data(device, FeederRecord))

            elif device_type in DEVICES_LITTER_BOX:
                main_tasks.append(
                    self._fetch_device_data(device, Litter),
                )
                record_tasks.append(self._fetch_device_data(device, LitterRecord))

                if device_type == T4:
                    record_tasks.append(self._fetch_device_data(device, LitterStats))
                if device_type == T6:
                    record_tasks.append(self._fetch_device_data(device, PetOutGraph))

            elif device_type in DEVICES_WATER_FOUNTAIN:
                main_tasks.append(self._fetch_device_data(device, WaterFountain))
                record_tasks.append(
                    self._fetch_device_data(device, WaterFountainRecord)
                )

            elif device_type in DEVICES_PURIFIER:
                main_tasks.append(self._fetch_device_data(device, Purifier))

        # Execute main device tasks first
        await asyncio.gather(*main_tasks)

        # Then execute record tasks
        await asyncio.gather(*record_tasks)

        # Add populate_pet_stats tasks
        stats_tasks = [
            self.populate_pet_stats(self.petkit_entities[device.device_id])
            for device in device_list
            if device.device_type.lower() in DEVICES_LITTER_BOX
        ]

        # Execute stats tasks
        await asyncio.gather(*stats_tasks)

        end_time = datetime.now()
        total_time = end_time - start_time
        _LOGGER.debug("Petkit data fetched successfully in: %s", total_time)

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
        """Fetch the device data from the PetKit servers."""
        device_type = device.device_type.lower()

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

        # Add the device type into dataclass
        if isinstance(device_data, list):
            for item in device_data:
                item.device_type = device_type
        else:
            device_data.device_type = device_type

        if data_class.data_type == DEVICE_DATA:
            self.petkit_entities[device.device_id] = device_data
            _LOGGER.debug("Device data fetched OK for %s", device_type)
        elif data_class.data_type == DEVICE_RECORDS:
            self.petkit_entities[device.device_id].device_records = device_data
            _LOGGER.debug("Device records fetched OK for %s", device_type)
        elif data_class.data_type == DEVICE_STATS:
            if device_type == T4:
                self.petkit_entities[device.device_id].device_stats = device_data
            if device_type == T6:
                self.petkit_entities[device.device_id].device_pet_graph_out = (
                    device_data
                )
            _LOGGER.debug("Device stats fetched OK for %s", device_type)
        else:
            _LOGGER.error("Unknown data type: %s", data_class.data_type)

    async def get_pets_list(self) -> list[Pet]:
        """Extract and return the list of pets."""
        return [
            entity
            for entity in self.petkit_entities.values()
            if isinstance(entity, Pet)
        ]

    @staticmethod
    def get_safe_value(value: int | None, default: int = 0) -> int:
        """Return the value if not None, otherwise return the default."""
        return value if value is not None else default

    @staticmethod
    def calculate_duration(start: int | None, end: int | None) -> int:
        """Calculate the duration, ensuring both start and end are not None."""
        if start is None or end is None:
            return 0
        return end - start

    async def populate_pet_stats(self, stats_data: Litter) -> None:
        """Collect data from litter data to populate pet stats."""

        pets_list = await self.get_pets_list()
        for pet in pets_list:
            if stats_data.device_type == T4 and stats_data.device_records:
                await self._process_t4(pet, stats_data.device_records)
            elif stats_data.device_type == T6 and stats_data.device_pet_graph_out:
                await self._process_t6(pet, stats_data.device_pet_graph_out)

    async def _process_t4(self, pet, device_records):
        """Process T4 device records."""
        for stat in device_records:
            if stat.pet_id == pet.pet_id and (
                pet.last_litter_usage is None
                or self.get_safe_value(stat.timestamp) > pet.last_litter_usage
            ):
                pet.last_litter_usage = stat.timestamp
                pet.last_measured_weight = self.get_safe_value(
                    stat.content.pet_weight if stat.content else None
                )
                pet.last_duration_usage = self.calculate_duration(
                    stat.content.time_in if stat.content else None,
                    stat.content.time_out if stat.content else None,
                )
                pet.last_device_used = "Pura Max"

    async def _process_t6(self, pet, pet_graphs):
        """Process T6 pet graphs."""
        for graph in pet_graphs:
            if graph.pet_id == pet.pet_id and (
                pet.last_litter_usage is None
                or self.get_safe_value(graph.time) > pet.last_litter_usage
            ):
                pet.last_litter_usage = graph.time
                pet.last_measured_weight = self.get_safe_value(
                    graph.content.pet_weight if graph.content else None
                )
                pet.last_duration_usage = self.get_safe_value(graph.toilet_time)
                pet.last_device_used = "Purobot Ultra"

    async def send_api_request(
        self,
        device_id: int,
        action: StrEnum,
        setting: dict | None = None,
    ) -> bool:
        """Control the device using the PetKit API."""
        await self.validate_session()

        device = self.petkit_entities.get(device_id)
        if not device:
            raise PypetkitError(f"Device with ID {device_id} not found.")

        _LOGGER.debug(
            "Control API device=%s id=%s action=%s param=%s",
            device.device_type,
            device_id,
            action,
            setting,
        )

        # Check if the device type is supported
        if device.device_type:
            device_type = device.device_type.lower()
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
        url = f"{device.device_type.lower()}/{endpoint}"

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

    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        """Initialize the request."""
        self.base_url = base_url
        self.session = session
        self.base_headers = self._generate_header()

    @staticmethod
    def _generate_header() -> dict[str, str]:
        """Create header for interaction with API endpoint."""

        return {
            "Accept": Header.ACCEPT.value,
            "Accept-Language": Header.ACCEPT_LANG,
            "Accept-Encoding": Header.ENCODING,
            "Content-Type": Header.CONTENT_TYPE,
            "User-Agent": Header.AGENT,
            "X-Img-Version": Header.IMG_VERSION,
            "X-Locale": Header.LOCALE,
            "X-Client": Header.CLIENT,
            "X-Hour": Header.HOUR,
            "X-TimezoneId": Header.TIMEZONE_ID,
            "X-Api-Version": Header.API_VERSION,
            "X-Timezone": Header.TIMEZONE,
        }

    async def request(
        self,
        method: str,
        url: str,
        params=None,
        data=None,
        headers=None,
    ) -> dict:
        """Make a request to the PetKit API."""
        _url = "/".join(s.strip("/") for s in [self.base_url, url])
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
        """Handle the response from the PetKit API."""
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise PetkitInvalidHTTPResponseCodeError(
                f"Request failed with status code {e.status}"
            ) from e

        try:
            response_json = await response.json()
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
                    raise PetkitAuthenticationUnregisteredEmailError(
                        f"Authentication failed: {error_msg}"
                    )
                case _:
                    raise PypetkitError(
                        f"Request failed code : {error_code} details : {error_msg}"
                    )

        # Check for success in the response
        if RES_KEY in response_json:
            return response_json[RES_KEY]

        raise PypetkitError("Unexpected response format")
