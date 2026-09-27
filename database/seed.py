# Module for populating database with initial test data.

import logging

from database.connection import DatabaseManager
from utils.helpers import hash_password, get_current_datetime
from utils.generators import generate_seat_numbers

logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with initial test data."""
    try:
        with DatabaseManager() as cursor:

            # Check if data already exists
            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
            count = cursor.fetchone()['cnt']

            if count > 0:
                logger.info("Database already seeded. Skipping.")
                return

            now = get_current_datetime()

            # ---- Seed Users ----

            users = [
                # Admin
                ("Admin", "Other", "admin@fastx.com", "9000000001",
                 "FastX HQ, Chennai", hash_password("admin123"), "ADMIN", True, now),

                # Bus Operators
                ("Rajesh Kumar", "Male", "rajesh@fastx.com", "9000000002",
                 "Anna Nagar, Chennai", hash_password("operator123"), "BUS_OPERATOR", True, now),

                ("Priya Transport", "Female", "priya@fastx.com", "9000000003",
                 "MG Road, Puducherry", hash_password("operator123"), "BUS_OPERATOR", True, now),

                # Regular Users
                ("Adhitya", "Male", "adhitya@gmail.com", "9876543210",
                 "Puducherry", hash_password("user123"), "USER", True, now),

                ("Sneha", "Female", "sneha@gmail.com", "9876543211",
                 "Chennai", hash_password("user123"), "USER", True, now),
            ]

            cursor.executemany("""
                INSERT INTO users (name, gender, email, phone, address, password, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, users)


            logger.info("Seeded %d users.", len(users))

            # ---- Seed Buses ----

            buses = [
                # Operator 1 (Rajesh Kumar, user_id=2)
                ("FastX Express", "TN01AB1234", "Sleeper AC", 40,
                 "Water Bottle,Charging Point,TV,Blanket", 2, True),  # Routine bus (Daily)

                ("FastX Deluxe", "TN01CD5678", "Semi-Sleeper", 36,
                 "Water Bottle,Charging Point", 2, False),  # Specific date bus (Long trip)

                # Operator 2 (Priya Transport, user_id=3)
                ("Priya Travels", "PY01EF9012", "Seat AC", 44,
                 "Water Bottle,Charging Point,WiFi", 3, True),  # Routine bus (Daily)

                ("Priya Express", "PY01GH3456", "Sleeper Non-AC", 32,
                 "Water Bottle,Blanket", 3, False),  # Specific date bus (Long trip)
            ]

            cursor.executemany("""
                INSERT INTO buses (bus_name, bus_number, bus_type, total_seats, amenities, operator_id, is_routine)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, buses)

            logger.info("Seeded %d buses.", len(buses))

            # ---- Seed Routes ----

            routes = [
                # Bus 1: FastX Express
                (1, "Puducherry", "Chennai", "2026-10-01", "08:00 PM", "11:30 PM", 650),
                (1, "Chennai", "Bangalore", "2026-10-02", "10:00 PM", "06:00 AM", 850),

                # Bus 2: FastX Deluxe
                (2, "Puducherry", "Madurai", "2026-10-01", "09:00 PM", "04:00 AM", 750),
                (2, "Chennai", "Coimbatore", "2026-10-03", "07:00 PM", "03:00 AM", 900),

                # Bus 3: Priya Travels
                (3, "Chennai", "Puducherry", "2026-10-01", "06:00 AM", "09:30 AM", 450),
                (3, "Bangalore", "Chennai", "2026-10-02", "11:00 PM", "05:00 AM", 800),

                # Bus 4: Priya Express
                (4, "Madurai", "Chennai", "2026-10-01", "08:30 PM", "05:00 AM", 550),
                (4, "Coimbatore", "Puducherry", "2026-10-03", "09:00 PM", "06:30 AM", 700),
            ]

            cursor.executemany("""
                INSERT INTO routes (bus_id, origin, destination, journey_date, departure_time, arrival_time, fare)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, routes)

            logger.info("Seeded %d routes.", len(routes))

            # ---- Seed Seats ----

            # Get all buses and generate seats
            cursor.execute("SELECT id, total_seats, bus_type FROM buses")
            all_buses = cursor.fetchall()

            total_seats_created = 0
            for bus in all_buses:
                bus_id = bus['id']
                num_seats = bus['total_seats']
                bus_type = bus['bus_type']

                seat_numbers = generate_seat_numbers(num_seats)

                # Determine seat type based on bus type
                seat_type = "SLEEPER" if "Sleeper" in bus_type else "SEAT"

                seat_data = [
                    (bus_id, seat_num, seat_type, "AVAILABLE")
                    for seat_num in seat_numbers
                ]

                cursor.executemany("""
                    INSERT INTO seats (bus_id, seat_number, seat_type, status)
                    VALUES (%s, %s, %s, %s)
                """, seat_data)

                total_seats_created += len(seat_data)

            logger.info("Seeded %d seats across %d buses.", total_seats_created, len(all_buses))

            print("\n  Database seeded successfully!")
            print(f"  → {len(users)} users, {len(buses)} buses, "
                  f"{len(routes)} routes, {total_seats_created} seats\n")

    except Exception as e:
        logger.error("Error seeding database: %s", str(e))
        raise
