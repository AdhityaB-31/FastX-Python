# Payment repository module for managing payment database CRUD operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_payment(booking_id, transaction_id, amount, payment_method,
                   status, payment_date, refund_amount=0):
    """Create a new payment record in the database."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            INSERT INTO payments (booking_id, transaction_id, amount,
                                  payment_method, status, payment_date, refund_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, transaction_id, amount, payment_method,
              status, payment_date, refund_amount))
        payment_id = cursor.lastrowid
        logger.info("Created payment: %s (ID: %d, Booking: %d)",
                     transaction_id, payment_id, booking_id)
        return payment_id


def find_by_booking(booking_id):
    """Find the payment for a specific booking."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM payments WHERE booking_id = %s",
            (booking_id,)
        )
        row = cursor.fetchone()
        return row if row else None


def find_by_transaction_id(transaction_id):
    """Find a payment by its transaction ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM payments WHERE transaction_id = %s",
            (transaction_id,)
        )
        row = cursor.fetchone()
        return row if row else None


def update_refund(booking_id, refund_amount, status="REFUNDED"):
    """Update refund information for a payment."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            UPDATE payments
            SET refund_amount = %s, status = %s
            WHERE booking_id = %s
        """, (refund_amount, status, booking_id))
        logger.info("Refund updated for booking ID %d: Rs. %s (%s)",
                     booking_id, refund_amount, status)
        return cursor.rowcount > 0


def get_all_payments():
    """Get all payments in system."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT p.*, bk.user_id, bk.status AS booking_status
            FROM payments p
            JOIN bookings bk ON p.booking_id = bk.id
            ORDER BY p.id DESC
        """)
        rows = cursor.fetchall()
        return rows

