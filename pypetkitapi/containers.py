"""Dataclasses container for petkit API."""

from pydantic import BaseModel, Field, model_validator


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
    type_code: int = Field(alias="typeCode")
    unique_id: str = Field(alias="uniqueId")


class Pet(BaseModel):
    """Dataclass for pet data.
    Subclass of AccountData.
    """

    avatar: str | None = None
    created_at: int = Field(alias="createdAt")
    pet_id: int = Field(alias="petId")
    id: int | None = None  # Fictive field (for HA compatibility) copied from id
    sn: int | None = None  # Fictive field (for HA compatibility) copied from id
    pet_name: str | None = Field(None, alias="petName")
    name: str | None = None  # Fictive field (for HA compatibility) copied from pet_name
    device_type: str = "pet"  # Fictive field (for HA compatibility) fixed
    firmware: str | None = None  # Fictive field (for HA compatibility) fixed

    @model_validator(mode="before")
    def populate_fictive_fields(cls, values):  # noqa: N805
        """Populate fictive fields based on other fields."""
        values["id"] = values.get("id") or values.get("petId")
        values["sn"] = values.get("sn") or values.get("id")
        values["name"] = values.get("name") or values.get("petName")
        return values


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
