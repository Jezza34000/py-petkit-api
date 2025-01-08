"""Dataclasses for Schedule."""

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from pypetkitapi.const import DEVICE_DATA, PetkitEndpoint
from pypetkitapi.containers import Device


class Owner(BaseModel):
    """Dataclass for Owner Data."""

    device_count: int | None = Field(0, alias="deviceCount")
    id: str | None = None
    pet_count: int | None = Field(0, alias="petCount")
    user_count: int | None = Field(0, alias="userCount")


class Type(BaseModel):
    """Dataclass for Type Data."""

    enable: int | None = None
    id: str | None = None
    img: str | None = None
    is_custom: int | None = Field(0, alias="isCustom")
    name: str | None = None
    priority: int | None = None
    repeat_option: str | None = Field(alias="repeatOption")
    rpt: str | None = None
    schedule_appoint: str | None = Field(alias="scheduleAppoint")
    with_device_type: str | None = Field(alias="withDeviceType")
    with_pet: int | None = Field(0, alias="withPet")


class Schedule(BaseModel):
    """Dataclass for Schedule Data."""

    data_type: ClassVar[str] = DEVICE_DATA

    alarm_before: int | None = Field(0, alias="alarmBefore")
    created_at: datetime | None = Field(None, alias="createdAt")
    device_id: str | None = Field(None, alias="deviceId")
    device_type: str | None = Field(None, alias="deviceType")
    id: str | None = None
    name: str | None = None
    owner: Owner | None = None
    repeat: str | None = None
    status: int | None = None
    time: datetime | None = None
    type: Type | None = None
    user_custom_id: int | None = Field(0, alias="userCustomId")

    @classmethod
    def get_endpoint(cls, device_type: str) -> str:
        """Get the endpoint URL for the given device type."""
        return PetkitEndpoint.SCHEDULE

    @classmethod
    def query_param(
        cls,
        device: Device,
        device_data: Any | None = None,
    ) -> dict:
        """Generate query parameters including request_date."""
        return {"limit": 20}
