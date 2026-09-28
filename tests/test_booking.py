# Tests for booking service and fare calculation.

import pytest

from services import booking_service, bus_service
from exceptions.custom_exceptions import (
    SeatNotAvailableError,
    BookingNotFoundError,
    InvalidInputError,
)
from models.booking import booking_generator, calculate_booking_total


class TestFareCalculation:
    """Test group for fare calculation functions."""

    @pytest.mark.parametrize(
        "fare,seats,expected",
        [
            (500, 1, 500),
            (500, 2, 1000),
            (750, 3, 2250),
            (650, 4, 2600),
            (100, 10, 1000),
        ]
    )
    def test_calculate_fare(self, fare, seats, expected):
        """Test fare calculation with parametrized values."""
        assert booking_service.calculate_fare(fare, seats) == expected

    def test_calculate_fare_default_seats(self):
        """Test fare calculation with default seats (1)."""
        assert booking_service.calculate_fare(500) == 500

    def test_calculate_total_args(self):
        """Test calculate_total with *args."""
        total = booking_service.calculate_total(500, 500, 100)
        assert total == 1100

    def test_calculate_total_single_arg(self):
        """Test calculate_total with single argument."""
        assert booking_service.calculate_total(750) == 750

    def test_calculate_total_no_args(self):
        """Test calculate_total with no arguments."""
        assert booking_service.calculate_total() == 0


class TestBookingFlow:
    """Test group for booking operations."""

    def test_book_ticket_success(self, registered_user, seeded_route):
        """Test successful ticket booking."""
        result = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1", "A2"]
        )

        assert result['booking_status'] == "CONFIRMED"
        assert result['payment_status'] == "SUCCESS"
        assert result['passenger_name'] == registered_user['name']
        assert "A1" in result['seats']
        assert "A2" in result['seats']
        assert result['total_amount'] == seeded_route['fare'] * 2

    def test_book_ticket_no_seats(self, registered_user, seeded_route):
        """Test booking with no seats selected."""
        with pytest.raises(InvalidInputError, match="at least one seat"):
            booking_service.book_ticket(
                registered_user, seeded_route['route_id'], []
            )

    def test_book_ticket_invalid_seat(self, registered_user, seeded_route):
        """Test booking with non-existent seat number."""
        with pytest.raises(SeatNotAvailableError, match="not found"):
            booking_service.book_ticket(
                registered_user, seeded_route['route_id'], ["Z99"]
            )

    def test_book_ticket_already_booked_seat(self, registered_user, seeded_route):
        """Test booking a seat that's already booked."""
        # Book seat A1
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )

        # Try to book A1 again
        with pytest.raises(SeatNotAvailableError, match="already booked"):
            booking_service.book_ticket(
                registered_user, seeded_route['route_id'], ["A1"]
            )

    def test_book_ticket_with_custom_journey_date(self, registered_user, seeded_route):
        """Test booking a ticket with a manually specified custom journey date."""
        custom_date = "2026-11-20"
        result = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["B1"], journey_date=custom_date
        )

        assert result['booking_status'] == "CONFIRMED"
        assert result['journey_date'] == custom_date

        # Retrieve booking details and verify the journey_date persisted correctly
        booking_details = booking_service.get_booking_details(result['booking_id'])
        assert booking_details['journey_date'] == custom_date

    def test_date_specific_seat_availability(self, registered_user, seeded_route):
        """Test that seats booked on one date remain available for another date."""
        bus_id = seeded_route['bus_id']
        route_id = seeded_route['route_id']

        date1 = "2026-09-30"
        date2 = "2026-09-29"

        # Book seat A1 for date1
        booking_service.book_ticket(
            registered_user, route_id, ["A1"], journey_date=date1
        )

        # On date1, seat A1 should be BOOKED
        booked_date1 = [s['seat_number'] for s in bus_service.get_booked_seats(bus_id, journey_date=date1)]
        assert "A1" in booked_date1

        # On date2, seat A1 should be AVAILABLE
        available_date2 = [s['seat_number'] for s in bus_service.get_available_seats(bus_id, journey_date=date2)]
        assert "A1" in available_date2

        # Another booking for date2 for seat A1 should succeed
        res2 = booking_service.book_ticket(
            registered_user, route_id, ["A1"], journey_date=date2
        )
        assert res2['booking_status'] == "CONFIRMED"
        assert res2['journey_date'] == date2




class TestCancellation:
    """Test group for booking cancellation."""

    def test_cancel_booking_success(self, registered_user, seeded_route):
        """Test successful booking cancellation."""
        # Create a booking
        confirmation = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )

        # Cancel it
        result = booking_service.cancel_booking(
            registered_user, confirmation['booking_id']
        )

        assert result['status'] == "CANCELLED"

    def test_cancel_nonexistent_booking(self, registered_user):
        """Test cancelling a non-existent booking."""
        with pytest.raises(BookingNotFoundError):
            booking_service.cancel_booking(registered_user, 99999)

    def test_cancel_already_cancelled(self, registered_user, seeded_route):
        """Test cancelling an already cancelled booking."""
        confirmation = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )
        booking_service.cancel_booking(registered_user, confirmation['booking_id'])

        with pytest.raises(InvalidInputError, match="Cannot cancel"):
            booking_service.cancel_booking(
                registered_user, confirmation['booking_id']
            )

    def test_seats_released_after_cancellation(self, registered_user, seeded_route):
        """Test that seats become available after cancellation."""
        # Book seat A1
        confirmation = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )

        # Verify A1 is booked
        booked = bus_service.get_booked_seats(seeded_route['bus_id'])
        booked_numbers = [s['seat_number'] for s in booked]
        assert "A1" in booked_numbers

        # Cancel booking
        booking_service.cancel_booking(registered_user, confirmation['booking_id'])

        # Verify A1 is available again
        available = bus_service.get_available_seats(seeded_route['bus_id'])
        available_numbers = [s['seat_number'] for s in available]
        assert "A1" in available_numbers


class TestBookingHistory:
    """Test group for booking history."""

    def test_booking_history_empty(self, registered_user):
        """Test booking history with no bookings."""
        history = booking_service.get_booking_history(registered_user['id'])
        assert history['booking_count'] == 0
        assert history['total_spent'] == 0

    def test_booking_history_with_bookings(self, registered_user, seeded_route):
        """Test booking history with multiple bookings."""
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A2"]
        )

        history = booking_service.get_booking_history(registered_user['id'])
        assert history['booking_count'] == 2
        assert history['total_spent'] == seeded_route['fare'] * 2


class TestGeneratorAndCollections:
    """Test group for generator and collection usage."""

    def test_booking_generator(self):
        """Test booking_generator yields items lazily."""
        bookings = [
            {"id": 1, "total_amount": 500},
            {"id": 2, "total_amount": 750},
        ]
        gen = booking_generator(bookings)
        assert next(gen) == bookings[0]
        assert next(gen) == bookings[1]
        with pytest.raises(StopIteration):
            next(gen)

    def test_calculate_booking_total_generator_expression(self):
        """Test calculate_booking_total uses generator expression."""
        bookings = [
            {"total_amount": 500},
            {"total_amount": 750},
            {"total_amount": 1000},
        ]
        total = calculate_booking_total(bookings)
        assert total == 2250

    def test_bookings_summary_defaultdict(self, registered_user, seeded_route):
        """Test booking summary uses defaultdict grouping."""
        # Create bookings
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )
        conf = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A2"]
        )
        booking_service.cancel_booking(registered_user, conf['booking_id'])

        summary = booking_service.get_bookings_summary(registered_user['id'])
        assert "CONFIRMED" in summary
        assert "CANCELLED" in summary

    def test_route_booking_stats_counter(self, registered_user, seeded_route):
        """Test route booking statistics use Counter."""
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )
        booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A2"]
        )

        stats = booking_service.get_route_booking_stats()
        assert stats[seeded_route['route_id']] == 2
