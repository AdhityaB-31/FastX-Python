# Bus service module for managing bus and seat operations.

import logging

from repositories import bus_repository, seat_repository
from decorators.decorators import log_action
from utils.generators import generate_seat_numbers
from models.seat import SeatIterator

logger = logging.getLogger(__name__)


@log_action
def add_bus(bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine=False):
    """Add a new bus and generate its seats."""
    existing = bus_repository.find_by_bus_number(bus_number)
    if existing:
        raise ValueError(f"Bus with number '{bus_number}' already exists.")

    bus_id = bus_repository.create_bus(
        bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine
    )

    seat_numbers = generate_seat_numbers(total_seats)
    seat_type = "SLEEPER" if "sleeper" in bus_type.lower() else "SEAT"

    seat_repository.create_seats(bus_id, seat_numbers, seat_type)

    logger.info("Added bus '%s' with %d seats (Routine: %s).", bus_name, total_seats, is_routine)
    return bus_id


def get_bus_details(bus_id):
    """Get detailed bus information."""
    return bus_repository.find_by_id(bus_id)


def get_operator_buses(operator_id):
    """Get all buses belonging to an operator."""
    return bus_repository.find_by_operator(operator_id)


def get_available_seats(bus_id):
    """Get all available seats for a bus."""
    return seat_repository.get_available_seats(bus_id)


def get_booked_seats(bus_id):
    """Get all booked seats for a bus."""
    return seat_repository.get_booked_seats(bus_id)


def get_all_seats(bus_id):
    """Get all seats for a bus."""
    return seat_repository.get_all_seats(bus_id)


def display_seats_with_iterator(bus_id):
    """Display seat layout using SeatIterator."""
    all_seats = get_all_seats(bus_id)
    if not all_seats:
        print("\n  No seats found for this bus.\n")
        return

    seat_iter = SeatIterator(all_seats)

    formatted_seats = []
    available_count = 0
    booked_count = 0

    for seat in seat_iter:
        seat_num = seat['seat_number']
        if seat['status'] == 'AVAILABLE':
            formatted_seats.append(f" {seat_num} ")
            available_count += 1
        else:
            formatted_seats.append(f"[{seat_num}]")
            booked_count += 1

    print(f"\n{'BUS SEAT LAYOUT':^65}")
    print("-" * 65)
    print(f"{'Legend:  A1  = Available  |  [A2] = Booked (Not Selectable)':^65}")
    print("-" * 65)

    for i in range(0, len(formatted_seats), 4):
        row = formatted_seats[i:i + 4]
        row_str = "   ".join(f"{s:^5}" for s in row)
        print(f"{row_str:^65}")

    print("-" * 65)
    summary_text = f"Summary: {available_count} Available, {booked_count} Booked"
    print(f"{summary_text:^65}\n")


def find_seats_by_numbers(bus_id, seat_numbers):
    """Find seat records by seat numbers for a bus."""
    return seat_repository.find_seats_by_numbers(bus_id, seat_numbers)


def update_seat_status(seat_id, status):
    """Update a seat status."""
    return seat_repository.update_seat_status(seat_id, status)


def reset_all_seats(bus_id):
    """Reset all seats for a bus to AVAILABLE status."""
    count = seat_repository.reset_all_seats(bus_id)
    logger.info("Reset %d seats for bus ID: %d", count, bus_id)
    return count
