"""Pypetkit Client: A Python library for interfacing with PetKit"""

from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
from http import HTTPMethod
import logging

import aiohttp
from aiohttp import ContentTypeError

from pypetkitapi.command import ACTIONS_MAP
from pypetkitapi.const import (
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    DEVICES_WATER_FOUNTAIN,
    ERR_KEY,
    LOGIN_DATA,
    RES_KEY,
    Header,
    PetkitEndpoint,
    PetkitURL,
)
from pypetkitapi.containers import AccountData, Device, RegionInfo, SessionInfo
from pypetkitapi.exceptions import PypetkitError
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

_LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """Petkit Client"""

    _base_url: str
    _session: SessionInfo | None = None
    _servers_list: list[RegionInfo] = []
    account_data: list[AccountData] = []
    device_list: list[Feeder | Litter | WaterFountain] = []

    def __init__(
        self,
        username: str,
        password: str,
        region: str,
        timezone: str,
    ) -> None:
        """Initialize the PetKit Client."""
        self.username = username
        self.password = password
        self.region = region
        self.timezone = timezone

    async def _generate_header(self) -> dict[str, str]:
        """Create header for interaction with devices."""
        session_id = self._session.id if self._session is not None else ""
        return {
            "Accept": Header.ACCEPT.value,
            "Accept-Language": Header.ACCEPT_LANG,
            "Accept-Encoding": Header.ENCODING,
            "Content-Type": Header.CONTENT_TYPE,
            "User-Agent": Header.AGENT,
            "X-Img-Version": Header.IMG_VERSION,
            "X-Locale": Header.LOCALE,
            "F-Session": session_id,
            "X-Session": session_id,
            "X-Client": Header.CLIENT,
            "X-Hour": Header.HOUR,
            "X-TimezoneId": Header.TIMEZONE_ID,
            "X-Api-Version": Header.API_VERSION,
            "X-Timezone": Header.TIMEZONE,
        }

    async def _get_api_server_list(self) -> None:
        """Get the list of API servers and set the base URL."""
        _LOGGER.debug("Getting API server list")
        prep_req = PrepReq(base_url=PetkitURL.REGION_SRV)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url="",
            headers=await self._generate_header(),
        )
        _LOGGER.debug("API server list: %s", response)
        self._servers_list = [
            RegionInfo(**region) for region in response.get("list", [])
        ]

    async def _get_base_url(self) -> None:
        """Find the region server for the specified region."""
        await self._get_api_server_list()
        _LOGGER.debug("Finding region server for region: %s", self.region)

        regional_server = next(
            (server for server in self._servers_list if server.name == self.region),
            None,
        )

        if regional_server:
            _LOGGER.debug(
                "Found server %s for region : %s", regional_server, self.region
            )
            self._base_url = regional_server.gateway
            return
        _LOGGER.debug("Region %s not found in server list", self.region)

    async def request_login_code(self) -> bool:
        """Request a login code to be sent to the user's email."""
        _LOGGER.debug("Requesting login code for username: %s", self.username)
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.GET_LOGIN_CODE,
            params={"username": self.username},
            headers=await self._generate_header(),
        )
        if response:
            _LOGGER.info("Login code sent to user's email")
            return True
        return False

    async def login(self, valid_code: str | None = None) -> None:
        """Login to the PetKit service and retrieve the appropriate server."""
        # Retrieve the list of servers
        await self._get_base_url()

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
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.LOGIN,
            data=data,
            headers=await self._generate_header(),
        )
        session_data = response["session"]
        self._session = SessionInfo(**session_data)

    async def refresh_session(self) -> None:
        """Refresh the session."""
        _LOGGER.debug("Refreshing session")
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.REFRESH_SESSION,
            headers=await self._generate_header(),
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
        return

    async def _get_account_data(self) -> None:
        """Get the account data from the PetKit service."""
        await self.validate_session()
        _LOGGER.debug("Fetching account data")
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.FAMILY_LIST,
            headers=await self._generate_header(),
        )
        self.account_data = [AccountData(**account) for account in response]

    async def get_devices_data(self) -> None:
        """Get the devices data from the PetKit servers."""
        if not self.account_data:
            await self._get_account_data()

        device_list: list[Device] = []
        for account in self.account_data:
            _LOGGER.debug("Fetching devices data for account: %s", account)
            if account.device_list:
                device_list.extend(account.device_list)

        _LOGGER.info("%s devices found for this account", len(device_list))
        for device in device_list:
            _LOGGER.debug("Fetching devices data: %s", device)
            device_type = device.device_type.lower()
            # TODO: Fetch device records
            if device_type in DEVICES_FEEDER:
                await self._fetch_device_data(device, Feeder)
            elif device_type in DEVICES_LITTER_BOX:
                await self._fetch_device_data(device, Litter)
            elif device_type in DEVICES_WATER_FOUNTAIN:
                await self._fetch_device_data(device, WaterFountain)
            else:
                _LOGGER.warning("Unknown device type: %s", device_type)

    async def _fetch_device_data(
        self,
        device: Device,
        data_class: type[Feeder | Litter | WaterFountain],
    ) -> None:
        """Fetch the device data from the PetKit servers."""
        await self.validate_session()
        endpoint = data_class.get_endpoint(device.device_type)
        device_type = device.device_type.lower()
        query_param = data_class.query_param(device.device_id)

        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url=f"{device_type}/{endpoint}",
            params=query_param,
            headers=await self._generate_header(),
        )
        device_data = data_class(**response)
        device_data.device_type = device.device_type  # Add the device_type attribute
        _LOGGER.info("Adding device type: %s", device.device_type)
        self.device_list.append(device_data)

    async def send_api_request(
        self,
        device: Feeder | Litter | WaterFountain,
        action: StrEnum,
        setting: dict | None = None,
    ) -> None:
        """Control the device using the PetKit API."""

        _LOGGER.debug(
            "Control API: %s %s %s",
            action,
            setting,
            device,
        )

        if device.device_type:
            device_type = device.device_type.lower()
        else:
            raise PypetkitError(
                "Device type is not available, and is mandatory for sending commands."
            )

        if action not in ACTIONS_MAP:
            raise PypetkitError(f"Action {action} not supported.")

        action_info = ACTIONS_MAP[action]
        if device_type not in action_info.supported_device:
            raise PypetkitError(
                f"Device type {device.device_type} not supported for action {action}."
            )

        if callable(action_info.endpoint):
            endpoint = action_info.endpoint(device)
        else:
            endpoint = action_info.endpoint
        url = f"{device.device_type.lower()}/{endpoint}"

        headers = await self._generate_header()

        # Use the lambda to generate params
        if setting is not None:
            params = action_info.params(device, setting)
        else:
            params = action_info.params(device)

        prep_req = PrepReq(base_url=self._base_url)
        await prep_req.request(
            method=HTTPMethod.POST,
            url=url,
            data=params,
            headers=headers,
        )


class PrepReq:
    """Prepare the request to the PetKit API."""

    def __init__(self, base_url: str, base_headers: dict | None = None) -> None:
        """Initialize the request."""
        self.base_url = base_url
        self.base_headers = base_headers or {}

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
        _LOGGER.debug(
            "Request: %s %s Params: %s Data: %s Headers: %s",
            method,
            _url,
            params,
            data,
            _headers,
        )
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    _url,
                    params=params,
                    data=data,
                    headers=_headers,
                ) as resp:
                    response = await resp.json()
                    if ERR_KEY in response:
                        error_msg = response[ERR_KEY].get("msg", "Unknown error")
                        raise PypetkitError(f"Request failed: {error_msg}")
                    if RES_KEY in response:
                        _LOGGER.debug("Request response: %s", response)
                        return response[RES_KEY]
                    raise PypetkitError("Unexpected response format")
            except ContentTypeError:
                """If we get an error, lets log everything for debugging."""
                try:
                    resp_json = await resp.json(content_type=None)
                    _LOGGER.info("Resp: %s", resp_json)
                except ContentTypeError as err_2:
                    _LOGGER.info(err_2)
                resp_raw = await resp.read()
                _LOGGER.info("Resp raw: %s", resp_raw)
                # Still raise the err so that it's clear it failed.
                raise
