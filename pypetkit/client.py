"""Pypetkit Client: A Python library for interfacing with PetKit"""

from datetime import datetime, timedelta
import hashlib
from http import HTTPMethod
import logging

import aiohttp
from aiohttp import ContentTypeError

from pypetkit.const import (
    CLIENT_NFO,
    ERROR_KEY,
    FEEDER,
    LITTER_BOX,
    RESULT_KEY,
    WATER_FOUNTAIN,
    Header,
    PetkitEndpoint,
    PetkitURL,
)
from pypetkit.containers import (
    AccountData,
    Device,
    FeederData,
    LitterData,
    RegionInfo,
    SessionInfo,
    WaterFountainData,
)
from pypetkit.exceptions import PypetkitError

_LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """Petkit Client"""

    _session: SessionInfo | None = None
    _account_data: AccountData | None = None
    _base_url: str | None = None

    Feeder: FeederData | None = None
    LitterBox: LitterData | None = None
    WaterFountain: WaterFountainData | None = None

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
        return {
            "Accept": Header.ACCEPT,
            "Accept-Language": Header.ACCEPT_LANG,
            "Accept-Encoding": Header.ENCODING,
            "Content-Type": Header.CONTENT_TYPE,
            "User-Agent": Header.AGENT,
            "X-Img-Version": Header.IMG_VERSION,
            "X-Locale": Header.LOCALE,
            "F-Session": self._session.id if self._session is not None else "",
            "X-Session": self._session.id if self._session is not None else "",
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
        region_data = response.get(RESULT_KEY)
        if isinstance(region_data, dict):
            servers = [
                RegionInfo.from_dict(region) for region in region_data.get("list", [])
            ]
            self.servers_dict = {server.name: server for server in servers}
            if self.region in self.servers_dict:
                _LOGGER.debug(
                    "Region %s found in server list using gateway %s",
                    self.region,
                    self.servers_dict[self.region].gateway,
                )
                self._base_url = self.servers_dict[self.region].gateway
                return
            raise PypetkitError(f"Region {self.region} not found in server list")
        raise PypetkitError("Failed to get API server list")

    async def login(self) -> None:
        """Login to the PetKit service and retrieve the appropriate server."""
        # Retrieve the list of servers
        await self._get_api_server_list()

        # Prepare the data to send
        data = {
            "client": str(CLIENT_NFO),
            "encrypt": "1",
            "oldVersion": Header.API_VERSION,
            "password": hashlib.md5(self.password.encode()).hexdigest(),  # noqa: S324
            "region": self.servers_dict[self.region].id,
            "username": self.username,
        }

        # Send the login request
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.POST,
            url=PetkitEndpoint.LOGIN,
            data=data,
            headers=await self._generate_header(),
        )

        if ERROR_KEY in response:
            error_msg = response[ERROR_KEY].get("msg", "Unknown error")
            raise PypetkitError(f"Login failed: {error_msg}")
        if RESULT_KEY in response:
            _LOGGER.debug("Login response OK : %s", response)
            session_data = response[RESULT_KEY]["session"]

            self._session = SessionInfo.from_dict(session_data)
            return
        raise PypetkitError("Unexpected login error")

    async def is_session_valid(self) -> bool:
        """Check if the session is still valid."""
        if self._session is None:
            return False
        created_at = datetime.strptime(
            self._session.created_at,
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )
        expires_in = timedelta(seconds=self._session.expires_in)
        expiration_time = created_at + expires_in
        current_time = datetime.now(tz=created_at.tzinfo)
        return current_time < expiration_time

    async def _get_account_data(self) -> None:
        """Get the account data from the PetKit service."""
        _LOGGER.debug("Fetching account data")
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url=PetkitEndpoint.FAMILY_LIST,
            headers=await self._generate_header(),
        )

        if RESULT_KEY in response:
            _LOGGER.debug("Account data response: %s", response)
            result_data = response[RESULT_KEY][0]  # Assuming there's only one result
            self._account_data = AccountData.from_dict(result_data)
            return
        raise PypetkitError("Failed to fetch account data")

    async def get_devices_data(self) -> None:
        """Get the devices data from the PetKit servers."""
        if not self._account_data:
            await self._get_account_data()

        devices = self._account_data.device_list
        for device in devices:
            _LOGGER.debug("Fetching devices data: %s", device)
            device_type = device.device_type.lower()
            if device_type in FEEDER:
                await self._fetch_device_data(device, FeederData)
            elif device_type in LITTER_BOX:
                await self._fetch_device_data(device, LitterData)
            elif device_type in WATER_FOUNTAIN:
                await self._fetch_device_data(device, WaterFountainData)
            else:
                _LOGGER.warning("Unknown device type: %s", device_type)

    async def _fetch_device_data(self, device: Device, data_class: type) -> None:
        """Fetch the device data from the PetKit servers."""
        endpoint = data_class.url_endpoint
        device_type = device.device_type.lower()
        query_param = data_class.query_param.copy()
        query_param["id"] = device.device_id

        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.GET,
            url=f"{device_type}/{endpoint}",
            params=query_param,
            headers=await self._generate_header(),
        )

        if ERROR_KEY in response:
            error_msg = response[ERROR_KEY].get("msg", "Unknown error")
            raise PypetkitError(f"Fetching device data failed: {error_msg}")
        if RESULT_KEY in response:
            _LOGGER.debug("Device data response: %s", response)
            if data_class == FeederData:
                self.Feeder = data_class.from_dict(response[RESULT_KEY])
            elif data_class == LitterData:
                self.LitterBox = data_class.from_dict(response[RESULT_KEY])
            return
        raise PypetkitError("Unexpected response while fetching device data")

    async def update_settings(self, device_id: str, command: str, data: dict) -> None:
        """Send a command to a PetKit device."""
        _LOGGER.debug(
            "Sending command %s to device %s with data %s",
            command,
            device_id,
            data,
        )
        prep_req = PrepReq(base_url=self._base_url)
        response = await prep_req.request(
            method=HTTPMethod.POST,
            url=f"{self._base_url}/{device_id}/{command}",
            data=data,
            headers=await self._generate_header(),
        )
        if ERROR_KEY in response:
            error_msg = response[ERROR_KEY].get("msg", "Unknown error")
            raise PypetkitError(f"Command {command} failed: {error_msg}")
        if RESULT_KEY in response:
            _LOGGER.debug("Command %s response: %s", command, response)
            return
        raise PypetkitError(f"Unexpected response from command {command}")


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
                    return await resp.json()
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
