# Route model class for FastX application.


class Route:
    """Represents a bus route in the FastX system."""

    def __init__(self, bus_id, origin, destination, journey_date,
                 departure_time, arrival_time, fare=0.0, route_id=None):
        """Initialize a Route instance."""
        self._route_id = route_id
        self._bus_id = bus_id
        self._origin = origin
        self._destination = destination
        self._journey_date = journey_date
        self._departure_time = departure_time
        self._arrival_time = arrival_time
        self._fare = fare

    @property
    def route_id(self):
        """Get the route's ID."""
        return self._route_id

    @route_id.setter
    def route_id(self, value):
        """Set the route's ID."""
        self._route_id = value

    @property
    def bus_id(self):
        """Get the associated bus ID."""
        return self._bus_id

    @property
    def origin(self):
        """Get the departure city."""
        return self._origin

    @origin.setter
    def origin(self, value):
        """Set the departure city."""
        self._origin = value

    @property
    def destination(self):
        """Get the arrival city."""
        return self._destination

    @destination.setter
    def destination(self, value):
        """Set the arrival city."""
        self._destination = value

    @property
    def journey_date(self):
        """Get the journey date."""
        return self._journey_date

    @journey_date.setter
    def journey_date(self, value):
        """Set the journey date."""
        self._journey_date = value

    @property
    def departure_time(self):
        """Get the departure time."""
        return self._departure_time

    @departure_time.setter
    def departure_time(self, value):
        """Set the departure time."""
        self._departure_time = value

    @property
    def arrival_time(self):
        """Get the arrival time."""
        return self._arrival_time

    @arrival_time.setter
    def arrival_time(self, value):
        """Set the arrival time."""
        self._arrival_time = value

    @property
    def fare(self):
        """Get the fare per seat."""
        return self._fare

    @fare.setter
    def fare(self, value):
        """Set the fare per seat."""
        if value < 0:
            raise ValueError("Fare cannot be negative.")
        self._fare = value

    def __str__(self):
        """Return string representation."""
        return (f"{self._origin} → {self._destination} "
                f"({self._journey_date}) - Rs. {self._fare}")

    def __repr__(self):
        """Return detailed representation."""
        return (f"Route(origin='{self._origin}', destination='{self._destination}', "
                f"journey_date='{self._journey_date}', fare={self._fare})")
