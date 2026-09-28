# Seat repository module for seat database CRUD operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_seats(bus_id, seat_numbers, seat_type):
    """Create seats for a bus in database."""
    with DatabaseManager() as cursor:
        for seat_num in seat_numbers:
            cursor.execute("""
                INSERT INTO seats (bus_id, seat_number, seat_type, status)
                VALUES (%s, %s, %s, 'AVAILABLE')
            """, (bus_id, seat_num, seat_type))


def _get_booked_seat_ids(bus_id, journey_date=None):
    """Get set of seat IDs that are booked for a given bus and optional journey date."""
    with DatabaseManager() as cursor:
        if journey_date:
            cursor.execute("""
                SELECT DISTINCT bs.seat_id
                FROM booking_seats bs
                JOIN bookings bk ON bs.booking_id = bk.id
                JOIN routes r ON bk.route_id = r.id
                WHERE r.bus_id = %s
                  AND bk.status = 'CONFIRMED'
                  AND COALESCE(bk.journey_date, r.journey_date) = %s
            """, (bus_id, journey_date))
        else:
            cursor.execute("""
                SELECT DISTINCT bs.seat_id
                FROM booking_seats bs
                JOIN bookings bk ON bs.booking_id = bk.id
                JOIN routes r ON bk.route_id = r.id
                WHERE r.bus_id = %s
                  AND bk.status = 'CONFIRMED'
            """, (bus_id,))
        rows = cursor.fetchall()
        return {row['seat_id'] for row in rows}


def get_available_seats(bus_id, journey_date=None):
    """Get available seats for a bus on a specific journey date."""
    all_seats = get_all_seats(bus_id, journey_date)
    return [s for s in all_seats if s['status'] == 'AVAILABLE']


def get_booked_seats(bus_id, journey_date=None):
    """Get booked seats for a bus on a specific journey date."""
    all_seats = get_all_seats(bus_id, journey_date)
    return [s for s in all_seats if s['status'] == 'BOOKED']


def get_all_seats(bus_id, journey_date=None):
    """Get all seats for a bus with dynamic status computed for the journey date."""
    booked_ids = _get_booked_seat_ids(bus_id, journey_date)
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT * FROM seats
            WHERE bus_id = %s
            ORDER BY seat_number
        """, (bus_id,))
        seats = cursor.fetchall()
        for s in seats:
            s['status'] = 'BOOKED' if s['id'] in booked_ids else 'AVAILABLE'
        return seats


def find_seats_by_numbers(bus_id, seat_numbers, journey_date=None):
    """Find seats by seat numbers for a bus on a specific journey date."""
    if not seat_numbers:
        return []
    all_seats = get_all_seats(bus_id, journey_date)
    number_set = set(seat_numbers)
    return [s for s in all_seats if s['seat_number'] in number_set]


def update_seat_status(seat_id, status):
    """Update a seat status."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            UPDATE seats SET status = %s WHERE id = %s
        """, (status, seat_id))
        return cursor.rowcount > 0


def reset_all_seats(bus_id):
    """Reset all seats for a bus to AVAILABLE status."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            UPDATE seats SET status = 'AVAILABLE' WHERE bus_id = %s
        """, (bus_id,))
        return cursor.rowcount


def count_available_seats(bus_id, journey_date=None):
    """Count available seats for a bus on a specific journey date."""
    return len(get_available_seats(bus_id, journey_date))
