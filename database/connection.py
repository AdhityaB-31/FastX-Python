# Module for managing database connection and transaction handling.

import logging
import mysql.connector
from mysql.connector import Error as MySQLError

logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Adhi@3129",
    "database": "fastx_python",
}


def get_connection():
    """Create and return a new MySQL database connection."""
    try:
        init_conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        init_cursor = init_conn.cursor()
        init_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`"
        )
        init_cursor.close()
        init_conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn

    except MySQLError as e:
        logger.error("Database connection error: %s", str(e))
        raise


class DatabaseManager:
    """Context manager for database transactions."""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                logger.error("Database transaction rolled back: %s", str(exc_val))
        except MySQLError as e:
            logger.error("Error during transaction handling: %s", str(e))
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

        return False

