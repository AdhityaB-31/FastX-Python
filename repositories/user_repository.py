# User repository module for managing user database operations.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_user(name, gender, email, phone, address, password, role, created_at, is_active=True):
    """Create a new user in the database."""
    with DatabaseManager() as cursor:
        cursor.execute("""
            INSERT INTO users (name, gender, email, phone, address, password, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, gender, email, phone, address, password, role, is_active, created_at))
        user_id = cursor.lastrowid
        logger.info("Created user: %s (ID: %d, Role: %s, Active: %s)", email, user_id, role, is_active)
        return user_id


def find_by_email(email):
    """Find a user by their email address."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        return row if row else None


def find_by_id(user_id):
    """Find a user by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        return row if row else None


def get_all_users(role=None):
    """Get all users, optionally filtered by role."""
    with DatabaseManager() as cursor:
        if role:
            cursor.execute(
                "SELECT * FROM users WHERE role = %s ORDER BY id",
                (role,)
            )
        else:
            cursor.execute("SELECT * FROM users ORDER BY id")
        rows = cursor.fetchall()
        return rows


def update_user(user_id, **kwargs):
    """Update user fields by ID."""
    if not kwargs:
        return False

    allowed_fields = {'name', 'gender', 'email', 'phone', 'address', 'password', 'is_active'}
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not fields:
        return False

    set_clause = ", ".join(f"{key} = %s" for key in fields)
    values = list(fields.values()) + [user_id]

    with DatabaseManager() as cursor:
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            values
        )
        logger.info("Updated user ID %d: %s", user_id, list(fields.keys()))
        return cursor.rowcount > 0


def delete_user(user_id):
    """Delete a user by database ID."""
    with DatabaseManager() as cursor:
        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )
        if cursor.rowcount > 0:
            logger.info("Deleted user ID: %d", user_id)
            return True
        return False


def email_exists(email):
    """Check if an email address is already registered."""
    user = find_by_email(email)
    return user is not None


def get_user_count(role=None):
    """Get count of users, optionally filtered by role."""
    with DatabaseManager() as cursor:
        if role:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM users WHERE role = %s",
                (role,)
            )
        else:
            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        return cursor.fetchone()['cnt']

