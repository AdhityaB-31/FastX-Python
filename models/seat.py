# Seat model class and SeatIterator for FastX application.


class Seat:
    """Represents an individual seat on a bus.

    Attributes:
        _seat_id (int): The seat's database ID.
        _bus_id (int): The associated bus ID.
        _seat_number (str): The seat number (e.g., 'A1', 'B3').
        _seat_type (str): The seat type ('SEAT' or 'SLEEPER').
        _status (str): The seat status ('AVAILABLE' or 'BOOKED').
    """

    def __init__(self, bus_id, seat_number, seat_type="SEAT",
                 status="AVAILABLE", seat_id=None):
        """Initialize a Seat instance.

        Args:
            bus_id: The associated bus ID.
            seat_number: The seat number (e.g., 'A1').
            seat_type: The seat type. Defaults to 'SEAT'.
            status: The seat status. Defaults to 'AVAILABLE'.
            seat_id: The seat's database ID.
        """
        self._seat_id = seat_id
        self._bus_id = bus_id
        self._seat_number = seat_number
        self._seat_type = seat_type
        self._status = status

    @property
    def seat_id(self):
        """Get the seat's ID."""
        return self._seat_id

    @seat_id.setter
    def seat_id(self, value):
        """Set the seat's ID."""
        self._seat_id = value

    @property
    def bus_id(self):
        """Get the associated bus ID."""
        return self._bus_id

    @property
    def seat_number(self):
        """Get the seat number."""
        return self._seat_number

    @property
    def seat_type(self):
        """Get the seat type."""
        return self._seat_type

    @property
    def status(self):
        """Get the seat status."""
        return self._status

    @status.setter
    def status(self, value):
        """Set the seat status."""
        valid_statuses = ['AVAILABLE', 'BOOKED']
        if value not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        self._status = value

    def is_available(self):
        """Check if the seat is available for booking."""
        return self._status == "AVAILABLE"

    def __str__(self):
        """Return string representation."""
        return f"{self._seat_number} ({self._status})"

    def __repr__(self):
        """Return detailed representation."""
        return (f"Seat(seat_number='{self._seat_number}', "
                f"status='{self._status}', bus_id={self._bus_id})")


class SeatIterator:
    """Custom iterator for iterating over a collection of seats.

    Demonstrates the iterator protocol with __iter__ and __next__.

    Usage:
        seats = [Seat(...), Seat(...), ...]
        for seat in SeatIterator(seats):
            print(seat)
    """

    def __init__(self, seats):
        """Initialize the SeatIterator.

        Args:
            seats: A list of Seat objects or seat data to iterate over.
        """
        self.seats = seats
        self.index = 0

    def __iter__(self):
        """Return the iterator object itself.

        Returns:
            SeatIterator: Self reference for the iterator protocol.
        """
        return self

    def __next__(self):
        """Return the next seat in the collection.

        Returns:
            Seat: The next seat object.

        Raises:
            StopIteration: When all seats have been iterated.
        """
        if self.index >= len(self.seats):
            raise StopIteration

        seat = self.seats[self.index]
        self.index += 1
        return seat
