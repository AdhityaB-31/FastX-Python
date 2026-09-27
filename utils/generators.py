# Generator utility module for transaction IDs, booking IDs, and seat numbers.

import uuid

from database.connection import get_connection


def generate_transaction_id():
    """Generate a unique transaction ID string."""
    return f"TXN-{uuid.uuid4().hex[:10].upper()}"


def generate_booking_id():
    """Generate next sequential booking ID string."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT MAX(id) AS max_id FROM bookings")
        result = cursor.fetchone()
        last_id = result['max_id'] if result['max_id'] is not None else 0
        next_num = 10001 + last_id
        return f"FXB{next_num}"
    except Exception:
        return f"FXB{10001}"
    finally:
        cursor.close()
        conn.close()


def generate_seat_numbers(total_seats, prefix_rows="ABCDEFGHIJ", seats_per_row=4):
    """Generate seat numbers in a grid pattern."""
    seats = []
    for row_index in range(len(prefix_rows)):
        for seat_num in range(1, seats_per_row + 1):
            if len(seats) >= total_seats:
                return seats
            seats.append(f"{prefix_rows[row_index]}{seat_num}")
    return seats

