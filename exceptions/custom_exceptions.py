# Module for custom exception classes in FastX application.



class FastXBaseError(Exception):
    """Base exception for all FastX application errors."""

    def __init__(self, message="An error occurred in FastX."):
        self.message = message
        super().__init__(self.message)


class SeatNotAvailableError(FastXBaseError):
    """Raised when a selected seat is not available for booking."""

    def __init__(self, message="The selected seat is not available."):
        super().__init__(message)


class BookingNotFoundError(FastXBaseError):
    """Raised when a booking cannot be found in the system."""

    def __init__(self, message="Booking not found."):
        super().__init__(message)


class UnauthorizedActionError(FastXBaseError):
    """Raised when a user attempts an action without proper authorization."""

    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__(message)


class InvalidJourneyDateError(FastXBaseError):
    """Raised when a journey date is invalid or in the past."""

    def __init__(self, message="Invalid journey date."):
        super().__init__(message)


class DuplicateEmailError(FastXBaseError):
    """Raised when attempting to register with an already existing email."""

    def __init__(self, message="An account with this email already exists."):
        super().__init__(message)


class InvalidCredentialsError(FastXBaseError):
    """Raised when login credentials are incorrect."""

    def __init__(self, message="Invalid email or password."):
        super().__init__(message)


class AccountInactiveError(InvalidCredentialsError):
    """Raised when an inactive user or operator attempts to log in."""

    def __init__(self, message="Account is inactive. Operator accounts require Admin activation."):
        super().__init__(message)


class RouteNotFoundError(FastXBaseError):
    """Raised when a route cannot be found in the system."""

    def __init__(self, message="Route not found."):
        super().__init__(message)


class InvalidInputError(FastXBaseError):
    """Raised when user input fails validation."""

    def __init__(self, message="Invalid input provided."):
        super().__init__(message)


class PaymentFailedError(FastXBaseError):
    """Raised when a payment processing attempt fails."""

    def __init__(self, message="Payment processing failed."):
        super().__init__(message)
