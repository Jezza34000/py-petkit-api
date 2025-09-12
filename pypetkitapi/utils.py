"""Utils functions for the PyPetKit API."""

import asyncio
from datetime import datetime
import importlib.metadata
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


def get_installed_packages():
    """Retrieve the complete list of Python packages installed in the current environ
    For debugging and resolving dependency conflicts.
    It captures the exact state of the environment at execution time, allowing
    identification of:
        - Incompatible versions between packages
        - Missing or conflicting dependencies
        - Duplicate installed packages
        - Versions not compliant with Home Assistant constraints
    Returns:
    list[str]: Alphabetically sorted list of packages in "name==version" format.
              Each element follows the standard pip freeze format (e.g., "requests==2.31.0").
              The list is sorted case-insensitively to facilitate reading and
    """
    packages = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        version = dist.version
        packages.append(f"{name}=={version}")

    packages.sort(key=str.lower)
    return packages
