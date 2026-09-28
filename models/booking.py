# Booking model class and generator functions for FastX application.


class Booking:
    """Represents a ticket booking in the FastX system."""

    # Booking status constants
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"

    def __init__(self, user_id, route_id, booking_date, total_amount=0.0,
                 status="CONFIRMED", booking_id=None):
        """Initialize a Booking instance."""
        self._booking_id = booking_id
        self._user_id = user_id
        self._route_id = route_id
        self._booking_date = booking_date
        self._total_amount = total_amount
        self._status = status

    @property
    def booking_id(self):
        """Get the booking's ID."""
        return self._booking_id

    @booking_id.setter
    def booking_id(self, value):
        """Set the booking's ID."""
        self._booking_id = value

    @property
    def user_id(self):
        """Get the user ID."""
        return self._user_id

    @property
    def route_id(self):
        """Get the route ID."""
        return self._route_id

    @property
    def booking_date(self):
        """Get the booking date."""
        return self._booking_date

    @property
    def total_amount(self):
        """Get the total booking amount."""
        return self._total_amount

    @total_amount.setter
    def total_amount(self, value):
        """Set the total booking amount."""
        self._total_amount = value

    @property
    def status(self):
        """Get the booking status."""
        return self._status

    @status.setter
    def status(self, value):
        """Set the booking status.

        Args:
            value: The new booking status.

        Raises:
            ValueError: If status is not a valid booking status.
        """
        valid_statuses = [
            self.CONFIRMED, self.CANCELLED,
            self.REFUND_PENDING, self.REFUNDED
        ]
        if value not in valid_statuses:
            raise ValueError(f"Invalid booking status. Must be one of: {valid_statuses}")
        self._status = value

    def is_cancellable(self):
        """Check if the booking can be cancelled."""
        return self._status == self.CONFIRMED

    def __str__(self):
        """Return string representation."""
        return (f"Booking FXB{10001 + (self._booking_id or 0) - 1}: "
                f"Rs. {self._total_amount} ({self._status})")

    def __repr__(self):
        """Return detailed representation."""
        return (f"Booking(booking_id={self._booking_id}, user_id={self._user_id}, "
                f"route_id={self._route_id}, total_amount={self._total_amount}, "
                f"status='{self._status}')")


def booking_generator(bookings):
    """Generator function that yields bookings one at a time.

    Demonstrates the generator pattern for lazy evaluation
    of booking collections.

    Args:
        bookings: An iterable of booking data (dicts or Booking objects).

    Yields:
        Individual booking items from the collection.
    """
    for booking in bookings:
        yield booking


def calculate_booking_total(bookings):
    """Calculate total amount across all bookings using a generator expression.

    Demonstrates generator expression syntax for efficient
    aggregation without creating an intermediate list.

    Args:
        bookings: An iterable of booking dicts with 'total_amount' key.

    Returns:
        float: The sum of all booking amounts.
    """
    # Generator expression - no intermediate list created
    return sum(
        booking['total_amount'] if isinstance(booking, dict) else booking.total_amount
        for booking in bookings
    )
