# Module for creating and managing database schema tables.

import logging

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables if they do not already exist."""
    try:
        with DatabaseManager() as cursor:

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(10) DEFAULT 'Other',
                    email VARCHAR(255) NOT NULL UNIQUE,
                    phone VARCHAR(15) NOT NULL,
                    address VARCHAR(255) DEFAULT '',
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'USER',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at VARCHAR(30) NOT NULL
                ) ENGINE=InnoDB
            """)

            cursor.execute("SHOW COLUMNS FROM users LIKE 'is_active'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")


            # Buses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bus_name VARCHAR(100) NOT NULL,
                    bus_number VARCHAR(20) NOT NULL UNIQUE,
                    bus_type VARCHAR(50) NOT NULL DEFAULT 'SEAT',
                    total_seats INT NOT NULL DEFAULT 40,
                    amenities VARCHAR(500) DEFAULT '',
                    operator_id INT NOT NULL,
                    is_routine BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (operator_id) REFERENCES users(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            cursor.execute("SHOW COLUMNS FROM buses LIKE 'is_routine'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE buses ADD COLUMN is_routine BOOLEAN NOT NULL DEFAULT FALSE")


            # Routes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bus_id INT NOT NULL,
                    origin VARCHAR(100) NOT NULL,
                    destination VARCHAR(100) NOT NULL,
                    journey_date VARCHAR(15) NOT NULL,
                    departure_time VARCHAR(15) NOT NULL,
                    arrival_time VARCHAR(15) NOT NULL,
                    fare DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (bus_id) REFERENCES buses(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            # Seats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bus_id INT NOT NULL,
                    seat_number VARCHAR(5) NOT NULL,
                    seat_type VARCHAR(10) NOT NULL DEFAULT 'SEAT',
                    status VARCHAR(15) NOT NULL DEFAULT 'AVAILABLE',
                    FOREIGN KEY (bus_id) REFERENCES buses(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            # Bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    route_id INT NOT NULL,
                    booking_date VARCHAR(15) NOT NULL,
                    journey_date VARCHAR(15),
                    total_amount DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (route_id) REFERENCES routes(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            cursor.execute("SHOW COLUMNS FROM bookings LIKE 'journey_date'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE bookings ADD COLUMN journey_date VARCHAR(15)")


            # Booking seats junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS booking_seats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_id INT NOT NULL,
                    seat_id INT NOT NULL,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (seat_id) REFERENCES seats(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            # Payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_id INT NOT NULL,
                    transaction_id VARCHAR(50) NOT NULL UNIQUE,
                    amount DECIMAL(10, 2) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL DEFAULT 'DUMMY_PAYMENT',
                    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
                    payment_date VARCHAR(30) NOT NULL,
                    refund_amount DECIMAL(10, 2) DEFAULT 0,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            logger.info("Database tables created successfully.")

    except Exception as e:
        logger.error("Error creating database tables: %s", str(e))
        raise
