"""Exception hierarchy."""


class GarfinhoError(Exception):
    """Base class for every error raised by this library."""


class ApiError(GarfinhoError):
    """The backend answered with an unexpected status or payload."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class AuthError(GarfinhoError):
    """Login failed, expired or was not completed."""


class LoginTimeoutError(AuthError):
    """The user did not finish the browser login in time."""


class NotAuthenticatedError(GarfinhoError):
    """An operation that needs a logged-in user was called without a session."""
