"""Utils functions for the PyPetKit API."""

from datetime import datetime
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_LOGGER = logging.getLogger(__name__)


def get_timezone_offset(timezone_user: str) -> str:
    """Get the timezone offset from its name. Return 0.0 if an error occurs."""
    try:
        timezone = ZoneInfo(timezone_user)
        now = datetime.now(timezone)
        offset = now.utcoffset()
        if offset is None:
            return "0.0"
        offset_in_hours = offset.total_seconds() / 3600
        return str(offset_in_hours)
    except (ZoneInfoNotFoundError, AttributeError) as e:
        _LOGGER.warning("Cannot get timezone offset for %s: %s", timezone_user, e)
        return "0.0"
