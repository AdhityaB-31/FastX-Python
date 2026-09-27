# Bus model class for FastX application.


class Bus:
    """Represents a bus in the FastX system."""

    def __init__(self, bus_name, bus_number, bus_type="SEAT",
                 total_seats=40, amenities="", operator_id=None,
                 is_routine=False, bus_id=None):
        self._bus_id = bus_id
        self._bus_name = bus_name
        self._bus_number = bus_number
        self._bus_type = bus_type
        self._total_seats = total_seats
        self._amenities = amenities
        self._operator_id = operator_id
        self._is_routine = is_routine

    @property
    def bus_id(self):
        """Get bus ID."""
        return self._bus_id

    @bus_id.setter
    def bus_id(self, value):
        """Set bus ID."""
        self._bus_id = value

    @property
    def bus_name(self):
        """Get bus name."""
        return self._bus_name

    @bus_name.setter
    def bus_name(self, value):
        """Set bus name."""
        self._bus_name = value

    @property
    def bus_number(self):
        """Get bus registration number."""
        return self._bus_number

    @bus_number.setter
    def bus_number(self, value):
        """Set bus registration number."""
        self._bus_number = value

    @property
    def bus_type(self):
        """Get bus type."""
        return self._bus_type

    @bus_type.setter
    def bus_type(self, value):
        """Set bus type."""
        self._bus_type = value

    @property
    def total_seats(self):
        """Get total seat count."""
        return self._total_seats

    @total_seats.setter
    def total_seats(self, value):
        """Set total seat count."""
        if value <= 0:
            raise ValueError("Total seats must be a positive number.")
        self._total_seats = value

    @property
    def amenities(self):
        """Get amenities string."""
        return self._amenities

    @amenities.setter
    def amenities(self, value):
        """Set amenities string."""
        self._amenities = value

    @property
    def operator_id(self):
        """Get operator user ID."""
        return self._operator_id

    @property
    def is_routine(self):
        """Get whether bus is a routine daily bus."""
        return self._is_routine

    @is_routine.setter
    def is_routine(self, value):
        """Set routine status."""
        self._is_routine = bool(value)

    def get_amenities_list(self):
        """Get amenities as a list."""
        if not self._amenities:
            return []
        return [a.strip() for a in self._amenities.split(",") if a.strip()]

    def __str__(self):
        """Return string representation."""
        routine_str = " (Routine Daily)" if self._is_routine else ""
        return f"{self._bus_name} ({self._bus_number}) - {self._bus_type}{routine_str}"

    def __repr__(self):
        """Return detailed representation."""
        return (f"Bus(bus_name='{self._bus_name}', bus_number='{self._bus_number}', "
                f"bus_type='{self._bus_type}', total_seats={self._total_seats}, "
                f"is_routine={self._is_routine})")