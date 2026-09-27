# Booking service module for managing ticket bookings, cancellations, and refunds.

import logging
from collections import defaultdict, Counter

from repositories import booking_repository, route_repository
from services import bus_service, payment_service
from utils.helpers import get_current_date, format_currency
from decorators.decorators import log_action, require_role
from exceptions.custom_exceptions import (
    SeatNotAvailableError,
    BookingNotFoundError,
    InvalidInputError,
)
from models.booking import booking_generator, calculate_booking_total

logger = logging.getLogger(__name__)


def calculate_total(*amounts):
    """Calculate total from multiple fare components."""
    return sum(amounts)


def calculate_fare(fare, seats=1):
    """Calculate total fare for given number of seats."""
    return fare * seats


@log_action
def book_ticket(current_user, route_id, seat_numbers):
    """Book tickets for specified seats on a route."""
    if not seat_numbers:
        raise InvalidInputError("Please select at least one seat.")

    route = route_repository.find_by_id(route_id)
    if route is None:
        raise InvalidInputError(f"Route {route_id} not found.")

    bus_id = route['bus_id']

    seats = bus_service.find_seats_by_numbers(bus_id, seat_numbers)

    if len(seats) != len(seat_numbers):
        found_numbers = {s['seat_number'] for s in seats}
        missing = [sn for sn in seat_numbers if sn not in found_numbers]
        raise SeatNotAvailableError(
            f"Seats not found: {', '.join(missing)}"
        )

    for seat in seats:
        if seat['status'] != 'AVAILABLE':
            raise SeatNotAvailableError(
                f"Seat {seat['seat_number']} is already booked."
            )

    fare_per_seat = route['fare']
    total_amount = calculate_total(
        *[fare_per_seat for _ in seat_numbers]
    )

    booking_date = get_current_date()
    booking_id = booking_repository.create_booking(
        user_id=current_user['id'],
        route_id=route_id,
        booking_date=booking_date,
        total_amount=total_amount,
        status="CONFIRMED"
    )

    seat_ids = [seat['id'] for seat in seats]
    booking_repository.add_booking_seats(booking_id, seat_ids)

    payment_result = payment_service.process_booking_payment(
        booking_id, total_amount
    )

    confirmation = {
        "booking_id": booking_id,
        "booking_display_id": f"FXB{10001 + booking_id - 1}",
        "passenger_name": current_user['name'],
        "bus_name": route['bus_name'],
        "bus_number": route['bus_number'],
        "operator_name": route.get('operator_name', 'N/A'),
        "origin": route['origin'],
        "destination": route['destination'],
        "journey_date": route['journey_date'],
        "departure_time": route['departure_time'],
        "seats": ", ".join(seat_numbers),
        "fare_per_seat": fare_per_seat,
        "total_amount": total_amount,
        "transaction_id": payment_result['transaction_id'],
        "payment_status": payment_result['status'],
        "booking_status": "CONFIRMED"
    }

    logger.info("Booking confirmed: %s - %d seats - Rs. %s",
                 confirmation['booking_display_id'], len(seat_numbers), total_amount)

    return confirmation


def get_booking_details(booking_id):
    """Get detailed booking information."""
    booking = booking_repository.find_by_id(booking_id)
    if booking is None:
        raise BookingNotFoundError(f"Booking with ID {booking_id} not found.")

    seats = booking_repository.get_booking_seats(booking_id)
    booking['seats'] = seats
    booking['seat_numbers'] = ", ".join(s['seat_number'] for s in seats)

    from repositories import payment_repository
    payment = payment_repository.find_by_booking(booking_id)
    booking['payment'] = payment

    return booking


@log_action
def get_booking_history(user_id):
    """Get booking history for a user."""
    bookings = booking_repository.find_by_user(user_id)

    booking_list = list(booking_generator(bookings))

    for booking in booking_list:
        seats = booking_repository.get_booking_seats(booking['id'])
        booking['seat_numbers'] = ", ".join(s['seat_number'] for s in seats)

    total_spent = calculate_booking_total(bookings)

    return {
        "bookings": booking_list,
        "total_spent": total_spent,
        "booking_count": len(booking_list)
    }


@log_action
def cancel_booking(current_user, booking_id):
    """Cancel a booking and release seats."""
    booking = booking_repository.find_by_id(booking_id)

    if booking is None:
        raise BookingNotFoundError(f"Booking {booking_id} not found.")

    if booking['user_id'] != current_user['id']:
        raise InvalidInputError("This booking does not belong to you.")

    if booking['status'] != 'CONFIRMED':
        raise InvalidInputError(
            f"Cannot cancel booking. Current status: {booking['status']}"
        )

    booking_repository.update_status(booking_id, "CANCELLED")

    booking_repository.release_booking_seats(booking_id)

    logger.info("Booking %d cancelled by user %d", booking_id, current_user['id'])

    return {
        "booking_id": booking_id,
        "booking_display_id": f"FXB{10001 + booking_id - 1}",
        "status": "CANCELLED",
        "total_amount": booking['total_amount']
    }


@log_action
def request_refund(current_user, booking_id):
    """Request a refund for a cancelled booking."""
    booking = booking_repository.find_by_id(booking_id)

    if booking is None:
        raise BookingNotFoundError(f"Booking {booking_id} not found.")

    if booking['user_id'] != current_user['id']:
        raise InvalidInputError("This booking does not belong to you.")

    if booking['status'] != 'CANCELLED':
        raise InvalidInputError(
            f"Refund can only be requested for cancelled bookings. "
            f"Current status: {booking['status']}"
        )

    refund_result = payment_service.process_refund(booking_id, booking['total_amount'])

    booking_repository.update_status(booking_id, "REFUNDED")

    return refund_result


def get_bookings_summary(user_id):
    """Get a summary of bookings grouped by status."""
    bookings = booking_repository.find_by_user(user_id)

    bookings_by_status = defaultdict(list)
    for booking in bookings:
        bookings_by_status[booking['status']].append(booking)

    return dict(bookings_by_status)


def get_route_booking_stats():
    """Get booking statistics per route."""
    all_bookings = booking_repository.get_all_bookings()

    route_ids = [b['route_id'] for b in all_bookings]
    route_count = Counter(route_ids)

    return route_count


@require_role("BUS_OPERATOR")
def get_operator_bookings(current_user):
    """Get all bookings for an operator's routes."""
    return booking_repository.get_bookings_by_operator(current_user['id'])


@require_role("BUS_OPERATOR")
def process_operator_refund(current_user, booking_id):
    """Process a refund as an operator."""
    booking = booking_repository.find_by_id(booking_id)

    if booking is None:
        raise BookingNotFoundError(f"Booking {booking_id} not found.")

    if booking['status'] not in ('CANCELLED', 'REFUND_PENDING'):
        raise InvalidInputError(
            f"Cannot process refund. Booking status: {booking['status']}"
        )

    refund_result = payment_service.process_refund(booking_id, booking['total_amount'])

    booking_repository.update_status(booking_id, "REFUNDED")

    return refund_result

