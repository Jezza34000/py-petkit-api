"""PyPetkit exceptions."""

from __future__ import annotations


class PypetkitError(Exception):
    """Class for PyPetkit exceptions."""


class PetkitTimeoutError(PypetkitError):
    """Class for PyPetkit timeout exceptions."""


class PetkitConnectionError(PypetkitError):
    """Class for PyPetkit connection exceptions."""
