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
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    DEVICES_WATER_FOUNTAIN,
    ERR_KEY,
    LOGIN_DATA,
    RES_KEY,
    SUCCESS_KEY,
    Header,
    PetkitDomain,
    PetkitEndpoint,
)
from pypetkitapi.containers import AccountData, Device, Pet, RegionInfo, SessionInfo
from pypetkitapi.exceptions import (
    PetkitAuthenticationError,
    PetkitInvalidHTTPResponseCodeError,
    PetkitInvalidResponseFormat,
    PetkitRegionalServerNotFoundError,
    PetkitTimeoutError,
    PypetkitError,
)
from pypetkitapi.feeder_container import Feeder, FeederRecord
from pypetkitapi.litter_container import Litter, LitterRecord
from pypetkitapi.water_fountain_container import WaterFountain, WaterFountainRecord

_LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """Petkit Client"""

    _session: SessionInfo | None = None
    account_data: list[AccountData] = []
    petkit_entities: dict[int, Feeder | Litter | WaterFountain | Pet] = {}

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
        )
        session_data = response["session"]
        self._session = SessionInfo(**session_data)

    async def validate_session(self) -> None:
        """Check if the session is still valid and refresh or re-login if necessary."""
        if self._session is None:
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
        start_time = datetime.now()
        if not self.account_data:
            await self._get_account_data()

        main_tasks = []
        record_tasks = []
        device_list: list[Device] = []

        for account in self.account_data:
            _LOGGER.debug("List devices data for account: %s", account)
            if account.device_list:
                device_list.extend(account.device_list)

            _LOGGER.debug("Fetch %s devices for this account", len(device_list))

            for device in device_list:
                device_type = device.device_type.lower()
                if device_type in DEVICES_FEEDER:
                    main_tasks.append(
                        self._fetch_device_data(account, device.device_id, Feeder)
                    )
                    record_tasks.append(
                        self._fetch_device_data(account, device.device_id, FeederRecord)
                    )
                elif device_type in DEVICES_LITTER_BOX:
                    main_tasks.append(
                        self._fetch_device_data(account, device.device_id, Litter)
                    )
                    record_tasks.append(
                        self._fetch_device_data(account, device.device_id, LitterRecord)
                    )
                elif device_type in DEVICES_WATER_FOUNTAIN:
                    main_tasks.append(
                        self._fetch_device_data(
                            account, device.device_id, WaterFountain
                        )
                    )
                    record_tasks.append(
                        self._fetch_device_data(
                            account, device.device_id, WaterFountainRecord
                        )
                    )

        # Execute main device tasks first
        await asyncio.gather(*main_tasks)

        # Then execute record tasks
        await asyncio.gather(*record_tasks)

        end_time = datetime.now()
        total_time = end_time - start_time
        _LOGGER.info("Petkit data fetched successfully in: %s", total_time)

    async def _fetch_device_data(
        self,
        account: AccountData,
        device_id: int,
        data_class: type[
            Feeder
            | Litter
            | WaterFountain
            | FeederRecord
            | LitterRecord
            | WaterFountainRecord
        ],
    ) -> None:
        """Fetch the device data from the PetKit servers."""
        await self.validate_session()
        device = None

        if account.device_list:
            device = next(
                (
                    device
                    for device in account.device_list
                    if device.device_id == device_id
                ),
                None,
            )
        if device is None:
            _LOGGER.error("Device not found: id=%s", device_id)
            return
        device_type = device.device_type.lower()

        _LOGGER.debug("Reading device type : %s (id=%s)", device_type, device_id)

        endpoint = data_class.get_endpoint(device_type)
        query_param = data_class.query_param(account, device.device_id)

        response = await self.req.request(
            method=HTTPMethod.POST,
            url=f"{device_type}/{endpoint}",
            params=query_param,
            headers=await self.get_session_id(),
        )

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
            self.petkit_entities[device_id] = device_data
            _LOGGER.debug("Device data fetched OK for %s", device_type)
        elif data_class.data_type == DEVICE_RECORDS:
            self.petkit_entities[device_id].device_records = device_data
            _LOGGER.debug("Device records fetched OK for %s", device_type)
        else:
            _LOGGER.error("Unknown data type: %s", data_class.data_type)

    async def send_api_request(
        self,
        device_id: int,
        action: StrEnum,
        setting: dict | None = None,
    ) -> None:
        """Control the device using the PetKit API."""
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
            raise PypetkitError(
                f"Device type {device.device_type} not supported for action {action}."
            )
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
        if res in (SUCCESS_KEY, RES_KEY):
            # TODO : Manage to get the response from manual feeding
            _LOGGER.debug("Command executed successfully")
        else:
            _LOGGER.error("Command execution failed")

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
            error_msg = response_json[ERR_KEY].get("msg", "Unknown error")
            if any(
                endpoint in url
                for endpoint in [
                    PetkitEndpoint.LOGIN,
                    PetkitEndpoint.GET_LOGIN_CODE,
                    PetkitEndpoint.REFRESH_SESSION,
                ]
            ):
                raise PetkitAuthenticationError(f"Login failed: {error_msg}")
            raise PypetkitError(f"Request failed: {error_msg}")

        # Check for success in the response
        if RES_KEY in response_json:
            return response_json[RES_KEY]

        raise PypetkitError("Unexpected response format")
