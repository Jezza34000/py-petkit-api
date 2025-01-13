"""PyPetkit exceptions."""

from __future__ import annotations


class PypetkitError(Exception):
    """Class for PyPetkit exceptions."""


class PetkitTimeoutError(PypetkitError):
    """Class for PyPetkit timeout exceptions."""


class PetkitSessionError(PypetkitError):
    """Class for PyPetkit connection exceptions."""


class PetkitSessionExpiredError(PypetkitError):
    """Class for PyPetkit connection exceptions."""


class PetkitAuthenticationUnregisteredEmailError(PypetkitError):
    """Exception raised when the email is not registered with Petkit."""

    def __init__(self, region: str):
        """Initialize the exception."""
        self.message = "The email you provided is not registered on Petkit's servers. Please check your email, or you are using the correct region."
        super().__init__(self.message)


class PetkitRegionalServerNotFoundError(PypetkitError):
    """Exception raised when the specified region server is not found."""

    def __init__(self, region: str):
        """Initialize the exception."""
        self.region = region
        self.message = (
            f"Region you provided: '{region}' was not found in the Petkit's server list. "
            f"Are you sure you provided the correct region ?"
        )
        super().__init__(self.message)


class PetkitInvalidHTTPResponseCodeError(PypetkitError):
    """Class for PyPetkit invalid HTTP Response exceptions."""


class PetkitInvalidResponseFormat(PypetkitError):
    """Class for PyPetkit invalid Response Format exceptions."""


class PetkitAuthenticationError(PypetkitError):
    """Class for PyPetkit authentication exceptions."""
