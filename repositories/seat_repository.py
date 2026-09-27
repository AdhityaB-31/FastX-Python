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


def get_available_seats(bus_id):
    """Get available seats for a bus."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT * FROM seats
            WHERE bus_id = %s AND status = 'AVAILABLE'
            ORDER BY seat_number
        """, (bus_id,))
        return cursor.fetchall()


def get_booked_seats(bus_id):
    """Get booked seats for a bus."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT * FROM seats
            WHERE bus_id = %s AND status = 'BOOKED'
            ORDER BY seat_number
        """, (bus_id,))
        return cursor.fetchall()


def get_all_seats(bus_id):
    """Get all seats for a bus."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT * FROM seats
            WHERE bus_id = %s
            ORDER BY seat_number
        """, (bus_id,))
        return cursor.fetchall()


def find_seats_by_numbers(bus_id, seat_numbers):
    """Find seats by seat numbers for a bus."""
    if not seat_numbers:
        return []
    with DatabaseManager() as cursor:
        placeholders = ",".join("%s" for _ in seat_numbers)
        cursor.execute(f"""
            SELECT * FROM seats
            WHERE bus_id = %s AND seat_number IN ({placeholders})
        """, [bus_id] + list(seat_numbers))
        return cursor.fetchall()


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


def count_available_seats(bus_id):
    """Count available seats for a bus."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM seats
            WHERE bus_id = %s AND status = 'AVAILABLE'
        """, (bus_id,))
        row = cursor.fetchone()
        return row['cnt'] if row else 0
