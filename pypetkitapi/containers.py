"""Dataclasses container for petkit API."""

from pydantic import BaseModel, Field, field_validator


class RegionInfo(BaseModel):
    """Dataclass for region data.
    Fetched from the API endpoint :
        - /v1/regionservers.
    """

    account_type: str = Field(alias="accountType")
    gateway: str
    id: str
    name: str


class BleRelay(BaseModel):
    """Dataclass for BLE relay devices
    Fetched from the API endpoint :
        - ble/ownSupportBleDevices
    """

    id: int
    low_version: int = Field(alias="lowVersion")
    mac: str
    name: str
    pim: int
    sn: str
    type_id: int = Field(alias="typeId")


class SessionInfo(BaseModel):
    """Dataclass for session data.
    Fetched from the API endpoint :
        - user/login
        - user/sendcodeforquicklogin
        - user/refreshsession
    """

    id: str
    user_id: str = Field(alias="userId")
    expires_in: int = Field(alias="expiresIn")
    region: str | None = None
    created_at: str = Field(alias="createdAt")
    refreshed_at: str | None = None


class Device(BaseModel):
    """Dataclass for device data.
    Subclass of AccountData.
    """

    created_at: int = Field(alias="createdAt")
    device_id: int = Field(alias="deviceId")
    device_name: str = Field(alias="deviceName")
    device_type: str = Field(alias="deviceType")
    group_id: int = Field(alias="groupId")
    type: int
    type_code: int = Field(0, alias="typeCode")
    unique_id: str = Field(alias="uniqueId")

    @field_validator("device_name", "device_type", "unique_id", mode="before")
    def convert_to_lower(cls, value):  # noqa: N805
        """Convert device_name, device_type and unique_id to lowercase."""
        if value is not None and isinstance(value, str):
            return value.lower()
        return value


class Pet(BaseModel):
    """Dataclass for pet data.
    Subclass of AccountData.
    """

    avatar: str
    created_at: int = Field(alias="createdAt")
    pet_id: int = Field(alias="petId")
    pet_name: str = Field(alias="petName")
    id: int | None = None  # Fictive field copied from id (for HA compatibility)
    sn: str | None = None  # Fictive field copied from id (for HA compatibility)
    name: str | None = None  # Fictive field copied from pet_name (for HA compatibility)
    firmware: str | None = None  # Fictive fixed field (for HA compatibility)
    device_nfo: Device | None = None  # Device is now optional

    # Litter stats
    last_litter_usage: int = 0
    last_device_used: str | None = None
    last_duration_usage: int = 0
    last_measured_weight: int = 0

    def __init__(self, **data):
        """Initialize the Pet dataclass.
        This method is used to fill the fictive fields after the standard initialization.
        """
        super().__init__(**data)
        self.id = self.id or self.pet_id
        self.sn = self.sn or str(self.id)
        self.name = self.name or self.pet_name


class User(BaseModel):
    """Dataclass for user data.
    Subclass of AccountData.
    """

    avatar: str | None = None
    created_at: int | None = Field(None, alias="createdAt")
    is_owner: int | None = Field(None, alias="isOwner")
    user_id: int | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")


class AccountData(BaseModel):
    """Dataclass for account data.
    Fetch from the API endpoint
        - /group/family/list.
    """

    device_list: list[Device] | None = Field(None, alias="deviceList")
    expired: bool | None = None
    group_id: int | None = Field(None, alias="groupId")
    name: str | None = None
    owner: int | None = None
    pet_list: list[Pet] | None = Field(None, alias="petList")
    user_list: list[User] | None = Field(None, alias="userList")


class CloudProduct(BaseModel):
    """Dataclass for cloud product details.
    Care+ Service for Smart devices with Camera.
    Subclass of many other device dataclasses.
    """

    charge_type: str | None = Field(None, alias="chargeType")
    name: str | None = None
    service_id: int | None = Field(None, alias="serviceId")
    subscribe: int | None = None
    work_indate: int | None = Field(None, alias="workIndate")
    work_time: int | None = Field(None, alias="workTime")


class Wifi(BaseModel):
    """Dataclass for Wi-Fi.
    Subclass of many other device dataclasses.
    """

    bssid: str | None = None
    rsq: int | None = None
    ssid: str | None = None


class FirmwareDetail(BaseModel):
    """Dataclass for firmware details.
    Subclass of many other device dataclasses.
    """

    module: str | None = None
    version: int | None = None
