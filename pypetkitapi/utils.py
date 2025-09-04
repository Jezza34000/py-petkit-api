"""Utils functions for the PyPetKit API."""

import asyncio
from datetime import datetime
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_LOGGER = logging.getLogger(__name__)


async def get_timezone_offset(timezone_user: str) -> str:
    """Get the timezone offset asynchronously."""

    def get_tz():
        try:
            tz = ZoneInfo(timezone_user)
            now = datetime.now(tz)
            offset = now.utcoffset()
            if offset is None:
                return "0.0"
            return str(offset.total_seconds() / 3600)
        except (ZoneInfoNotFoundError, AttributeError) as e:
            _LOGGER.warning(
                "Cannot get timezone offset for '%s' ZoneInfo return : %s",
                timezone_user,
                e,
            )
            return "0.0"

    return await asyncio.to_thread(get_tz)
