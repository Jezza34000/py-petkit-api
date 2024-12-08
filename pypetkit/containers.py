"""Dataclasses container for petkit API."""

from pydantic import BaseModel, Field


class RegionInfo(BaseModel):
    """Dataclass for region data."""

    account_type: str | None = Field(None, alias="accountType")
    gateway: str | None = None
    id: str | None = None
    name: str | None = None


class SessionInfo(BaseModel):
    """Dataclass for session data."""

    id: str
    user_id: str | None = Field(None, alias="userId")
    expires_in: int | None = Field(None, alias="expiresIn")
    region: str
    created_at: str | None = Field(None, alias="createdAt")


class Device(BaseModel):
    """Dataclass for device data."""

    created_at: int | None = Field(None, alias="createdAt")
    device_id: int | None = Field(None, alias="deviceId")
    device_name: str | None = Field(None, alias="deviceName")
    device_type: str | None = Field(None, alias="deviceType")
    group_id: int | None = Field(None, alias="groupId")
    type: int | None = None
    type_code: int | None = Field(None, alias="typeCode")
    unique_id: str | None = Field(None, alias="uniqueId")


class Pet(BaseModel):
    """Dataclass for pet data."""

    avatar: str | None = None
    created_at: int | None = Field(None, alias="createdAt")
    pet_id: int | None = Field(None, alias="petId")
    pet_name: str | None = Field(None, alias="petName")


class User(BaseModel):
    """Dataclass for user data."""

    avatar: str | None = None
    created_at: int | None = Field(None, alias="createdAt")
    is_owner: int | None = Field(None, alias="isOwner")
    user_id: int | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")


class AccountData(BaseModel):
    """Dataclass for account data."""

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
    """

    charge_type: str | None = Field(None, alias="chargeType")
    name: str | None = None
    service_id: int | None = Field(None, alias="serviceId")
    subscribe: int | None = None
    work_indate: int | None = Field(None, alias="workIndate")
    work_time: int | None = Field(None, alias="workTime")


class Wifi(BaseModel):
    """Dataclass for Wi-Fi."""

    bssid: str | None = None
    rsq: int | None = None
    ssid: str | None = None


class FirmwareDetail(BaseModel):
    """Dataclass for firmware details."""

    module: str | None = None
    version: int | None = None
