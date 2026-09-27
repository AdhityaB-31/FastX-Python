# Route repository module for managing route database CRUD operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_route(bus_id, origin, destination, journey_date,
                 departure_time, arrival_time, fare):
    """Create a new route in the database."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            INSERT INTO routes (bus_id, origin, destination, journey_date,
                               departure_time, arrival_time, fare)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (bus_id, origin, destination, journey_date,
              departure_time, arrival_time, fare))
        route_id = cursor.lastrowid
        logger.info("Created route: %s → %s (ID: %d)", origin, destination, route_id)
        return route_id


def find_by_id(route_id):
    """Find a route by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT r.*, b.bus_name, b.bus_number, b.bus_type,
                   b.total_seats, b.amenities, b.operator_id, b.is_routine,
                   op.name AS operator_name
            FROM routes r
            JOIN buses b ON r.bus_id = b.id
            LEFT JOIN users op ON b.operator_id = op.id
            WHERE r.id = %s
        """, (route_id,))
        row = cursor.fetchone()
        return row if row else None


def search_routes(**filters):
    """Search routes using keyword filters."""
    query = """
        SELECT r.*, b.bus_name, b.bus_number, b.bus_type,
               b.total_seats, b.amenities, b.operator_id, b.is_routine,
               op.name AS operator_name
        FROM routes r
        JOIN buses b ON r.bus_id = b.id
        LEFT JOIN users op ON b.operator_id = op.id
        WHERE 1=1
    """
    params = []

    if 'origin' in filters and filters['origin']:
        query += " AND LOWER(r.origin) = LOWER(%s)"
        params.append(filters['origin'])

    if 'destination' in filters and filters['destination']:
        query += " AND LOWER(r.destination) = LOWER(%s)"
        params.append(filters['destination'])

    if 'journey_date' in filters and filters['journey_date']:
        query += " AND (b.is_routine = TRUE OR r.journey_date = %s)"
        params.append(filters['journey_date'])

    if 'bus_type' in filters and filters['bus_type']:
        query += " AND LOWER(b.bus_type) = LOWER(%s)"
        params.append(filters['bus_type'])

    if 'min_fare' in filters and filters['min_fare'] is not None:
        query += " AND r.fare >= %s"
        params.append(filters['min_fare'])

    if 'max_fare' in filters and filters['max_fare'] is not None:
        query += " AND r.fare <= %s"
        params.append(filters['max_fare'])

    query += " ORDER BY r.fare ASC"

    with DatabaseManager() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows


def get_all_routes():
    """Get all routes with bus information."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT r.*, b.bus_name, b.bus_number, b.bus_type,
                   b.total_seats, b.amenities, b.operator_id, b.is_routine,
                   op.name AS operator_name
            FROM routes r
            JOIN buses b ON r.bus_id = b.id
            LEFT JOIN users op ON b.operator_id = op.id
            ORDER BY r.journey_date, r.departure_time
        """)
        rows = cursor.fetchall()
        return rows


def get_routes_by_operator(operator_id):
    """Get all routes for a specific operator."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            SELECT r.*, b.bus_name, b.bus_number, b.bus_type,
                   b.total_seats, b.amenities, b.operator_id, b.is_routine,
                   op.name AS operator_name
            FROM routes r
            JOIN buses b ON r.bus_id = b.id
            LEFT JOIN users op ON b.operator_id = op.id
            WHERE b.operator_id = %s
            ORDER BY r.journey_date, r.departure_time
        """, (operator_id,))
        rows = cursor.fetchall()
        return rows


def update_route(route_id, **kwargs):
    """Update route fields by ID."""
    if not kwargs:
        return False

    allowed_fields = {'origin', 'destination', 'journey_date',
                      'departure_time', 'arrival_time', 'fare'}
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not fields:
        return False

    set_clause = ", ".join(f"{key} = %s" for key in fields)
    values = list(fields.values()) + [route_id]

    with DatabaseManager() as cursor:
        cursor.execute(
            f"UPDATE routes SET {set_clause} WHERE id = %s",
            values
        )
        logger.info("Updated route ID %d: %s", route_id, list(fields.keys()))
        return cursor.rowcount > 0


def delete_route(route_id):
    """Delete a route by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "DELETE FROM routes WHERE id = %s",
            (route_id,)
        )
        if cursor.rowcount > 0:
            logger.info("Deleted route ID: %d", route_id)
            return True
        return False

