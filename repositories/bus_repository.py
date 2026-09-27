# Bus repository module for managing bus database CRUD operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_bus(bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine=False):
    """Create a new bus in the database."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            INSERT INTO buses (bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine))
        bus_id = cursor.lastrowid
        logger.info("Created bus: %s (ID: %d, Routine: %s)", bus_name, bus_id, is_routine)
        return bus_id


def find_by_id(bus_id):
    """Find a bus by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM buses WHERE id = %s",
            (bus_id,)
        )
        row = cursor.fetchone()
        return row if row else None


def find_by_operator(operator_id):
    """Find all buses belonging to an operator."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM buses WHERE operator_id = %s ORDER BY id",
            (operator_id,)
        )
        rows = cursor.fetchall()
        return rows


def find_by_bus_number(bus_number):
    """Find a bus by registration number."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM buses WHERE bus_number = %s",
            (bus_number,)
        )
        row = cursor.fetchone()
        return row if row else None


def get_all_buses():
    """Get all buses in system."""
    with DatabaseManager() as cursor:
        cursor.execute("SELECT * FROM buses ORDER BY id")
        rows = cursor.fetchall()
        return rows


def update_bus(bus_id, **kwargs):
    """Update bus fields by ID."""
    if not kwargs:
        return False

    allowed_fields = {'bus_name', 'bus_number', 'bus_type', 'total_seats', 'amenities', 'is_routine'}
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not fields:
        return False

    set_clause = ", ".join(f"{key} = %s" for key in fields)
    values = list(fields.values()) + [bus_id]

    with DatabaseManager() as cursor:
        cursor.execute(
            f"UPDATE buses SET {set_clause} WHERE id = %s",
            values
        )
        logger.info("Updated bus ID %d: %s", bus_id, list(fields.keys()))
        return cursor.rowcount > 0


def delete_bus(bus_id):
    """Delete a bus by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "DELETE FROM buses WHERE id = %s",
            (bus_id,)
        )
        if cursor.rowcount > 0:
            logger.info("Deleted bus ID: %d", bus_id)
            return True
        return False



