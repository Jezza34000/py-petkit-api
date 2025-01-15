import unittest
from pypetkitapi.exceptions import (
    PypetkitError,
    PetkitTimeoutError,
    PetkitSessionExpiredError,
    PetkitAuthenticationUnregisteredEmailError,
    PetkitRegionalServerNotFoundError,
    PetkitInvalidHTTPResponseCodeError,
    PetkitInvalidResponseFormat,
    PetkitAuthenticationError,
)


class TestPypetkitExceptions(unittest.TestCase):

    def test_pypetkit_error(self):
        with self.assertRaises(PypetkitError):
            raise PypetkitError("General error")

    def test_petkit_timeout_error(self):
        with self.assertRaises(PetkitTimeoutError):
            raise PetkitTimeoutError("Timeout error")

    def test_petkit_session_expired_error(self):
        with self.assertRaises(PetkitSessionExpiredError):
            raise PetkitSessionExpiredError("Session expired")

    def test_petkit_authentication_unregistered_email_error(self):
        with self.assertRaises(PetkitAuthenticationUnregisteredEmailError):
            raise PetkitAuthenticationUnregisteredEmailError

    def test_petkit_regional_server_not_found_error(self):
        with self.assertRaises(PetkitRegionalServerNotFoundError) as context:
            raise PetkitRegionalServerNotFoundError("us-west")
        self.assertEqual(context.exception.region, "us-west")
        self.assertIn(
            "Region you provided: 'us-west' was not found", context.exception.message
        )

    def test_petkit_invalid_http_response_code_error(self):
        with self.assertRaises(PetkitInvalidHTTPResponseCodeError):
            raise PetkitInvalidHTTPResponseCodeError("Invalid HTTP response code")

    def test_petkit_invalid_response_format(self):
        with self.assertRaises(PetkitInvalidResponseFormat):
            raise PetkitInvalidResponseFormat("Invalid response format")

    def test_petkit_authentication_error(self):
        with self.assertRaises(PetkitAuthenticationError):
            raise PetkitAuthenticationError("Authentication error")


if __name__ == "__main__":
    unittest.main()
