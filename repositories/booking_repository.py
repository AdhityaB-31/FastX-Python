# Booking repository module for managing booking database CRUD operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_booking(user_id, route_id, booking_date, total_amount, status="CONFIRMED"):
    """Create a new booking in the database."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            INSERT INTO bookings (user_id, route_id, booking_date, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, route_id, booking_date, total_amount, status))
        booking_id = cursor.lastrowid
        logger.info("Created booking ID: %d for user ID: %d", booking_id, user_id)
        return booking_id


def add_booking_seats(booking_id, seat_ids):
    """Add seats to a booking and mark them booked."""
    with DatabaseManager() as cursor:
        for seat_id in seat_ids:
            cursor.execute("""
                INSERT INTO booking_seats (booking_id, seat_id)
                VALUES (%s, %s)
            """, (booking_id, seat_id))

            cursor.execute("""
                UPDATE seats SET status = 'BOOKED' WHERE id = %s
            """, (seat_id,))

        logger.info("Added %d seats to booking ID: %d", len(seat_ids), booking_id)


def find_by_id(booking_id):
    """Find a booking by database ID with route and user details."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT bk.*, r.origin, r.destination, r.journey_date,
                   r.departure_time, r.arrival_time, r.fare,
                   b.bus_name, b.bus_number, b.bus_type,
                   u.name AS passenger_name, u.email AS passenger_email,
                   op.name AS operator_name
            FROM bookings bk
            JOIN routes r ON bk.route_id = r.id
            JOIN buses b ON r.bus_id = b.id
            JOIN users u ON bk.user_id = u.id
            LEFT JOIN users op ON b.operator_id = op.id
            WHERE bk.id = %s
        """, (booking_id,))
        row = cursor.fetchone()
        return row if row else None


def find_by_user(user_id):
    """Find all bookings for a user."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT bk.*, r.origin, r.destination, r.journey_date,
                   r.departure_time, r.arrival_time, r.fare,
                   b.bus_name, b.bus_number, b.bus_type,
                   op.name AS operator_name
            FROM bookings bk
            JOIN routes r ON bk.route_id = r.id
            JOIN buses b ON r.bus_id = b.id
            LEFT JOIN users op ON b.operator_id = op.id
            WHERE bk.user_id = %s
            ORDER BY bk.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        return rows


def get_booking_seats(booking_id):
    """Get seats associated with a booking."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT s.id, s.seat_number, s.seat_type, s.status, s.bus_id
            FROM booking_seats bs
            JOIN seats s ON bs.seat_id = s.id
            WHERE bs.booking_id = %s
        """, (booking_id,))
        rows = cursor.fetchall()
        return rows


def update_status(booking_id, status):
    """Update booking status."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            UPDATE bookings SET status = %s WHERE id = %s
        """, (status, booking_id))
        logger.info("Updated booking ID %d status to: %s", booking_id, status)
        return cursor.rowcount > 0


def release_booking_seats(booking_id):
    """Release all seats for a cancelled booking."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT seat_id FROM booking_seats WHERE booking_id = %s
        """, (booking_id,))
        seat_rows = cursor.fetchall()

        for row in seat_rows:
            cursor.execute("""
                UPDATE seats SET status = 'AVAILABLE' WHERE id = %s
            """, (row['seat_id'],))

        logger.info("Released %d seats for booking ID: %d",
                     len(seat_rows), booking_id)


def get_all_bookings():
    """Get all bookings in system with full details."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT bk.*, r.origin, r.destination, r.journey_date,
                   r.departure_time, r.arrival_time, r.fare,
                   b.bus_name, b.bus_number, b.bus_type,
                   u.name AS passenger_name, u.email AS passenger_email,
                   op.name AS operator_name
            FROM bookings bk
            JOIN routes r ON bk.route_id = r.id
            JOIN buses b ON r.bus_id = b.id
            JOIN users u ON bk.user_id = u.id
            LEFT JOIN users op ON b.operator_id = op.id
            ORDER BY bk.id DESC
        """)
        rows = cursor.fetchall()
        return rows


def get_bookings_by_route(route_id):
    """Get all bookings for a specific route."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT bk.*, u.name AS passenger_name, u.email AS passenger_email
            FROM bookings bk
            JOIN users u ON bk.user_id = u.id
            WHERE bk.route_id = %s
            ORDER BY bk.id DESC
        """, (route_id,))
        rows = cursor.fetchall()
        return rows


def get_bookings_by_operator(operator_id):
    """Get all bookings for an operator's routes."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT bk.*, r.origin, r.destination, r.journey_date,
                   r.departure_time, r.fare,
                   b.bus_name, b.bus_number,
                   u.name AS passenger_name, u.email AS passenger_email,
                   op.name AS operator_name
            FROM bookings bk
            JOIN routes r ON bk.route_id = r.id
            JOIN buses b ON r.bus_id = b.id
            JOIN users u ON bk.user_id = u.id
            LEFT JOIN users op ON b.operator_id = op.id
            WHERE b.operator_id = %s
            ORDER BY bk.id DESC
        """, (operator_id,))
        rows = cursor.fetchall()
        return rows

