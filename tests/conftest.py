"""
Pytest configuration and shared fixtures for FastX tests.

Provides:
- Isolated MySQL test database fixture
- Sample object fixtures
- Database setup/teardown for test isolation
"""

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database.connection as db_conn
from database.schema import create_tables


@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up an isolated MySQL test database for each test.

    Creates a temporary test database, runs tests, then drops it.

    Yields:
        None: Test runs with isolated database.
    """
    import mysql.connector

    test_db_name = "fastx_python_test"

    # Save original config
    original_config = db_conn.DB_CONFIG.copy()

    # Create test database
    init_conn = mysql.connector.connect(
        host=original_config["host"],
        port=original_config["port"],
        user=original_config["user"],
        password=original_config["password"],
    )
    init_cursor = init_conn.cursor()
    init_cursor.execute(f"DROP DATABASE IF EXISTS `{test_db_name}`")
    init_cursor.execute(f"CREATE DATABASE `{test_db_name}`")
    init_cursor.close()
    init_conn.close()

    # Override DB config for testing
    db_conn.DB_CONFIG["database"] = test_db_name

    # Create tables in test DB
    create_tables()

    yield

    # Drop test database
    try:
        cleanup_conn = mysql.connector.connect(
            host=original_config["host"],
            port=original_config["port"],
            user=original_config["user"],
            password=original_config["password"],
        )
        cleanup_cursor = cleanup_conn.cursor()
        cleanup_cursor.execute(f"DROP DATABASE IF EXISTS `{test_db_name}`")
        cleanup_cursor.close()
        cleanup_conn.close()
    except Exception:
        pass

    # Restore original config
    db_conn.DB_CONFIG.update(original_config)


@pytest.fixture
def sample_user_data():
    """Provide sample user registration data.

    Returns:
        dict: Sample user data for testing.
    """
    return {
        "name": "Test User",
        "gender": "Male",
        "email": "testuser@gmail.com",
        "phone": "9876543210",
        "address": "Test Address, Chennai",
        "password": "testpass123",
        "role": "USER"
    }


@pytest.fixture
def sample_operator_data():
    """Provide sample bus operator data.

    Returns:
        dict: Sample operator data for testing.
    """
    return {
        "name": "Test Operator",
        "gender": "Male",
        "email": "testop@fastx.com",
        "phone": "9876543211",
        "address": "Test Road, Puducherry",
        "password": "operator123",
        "role": "BUS_OPERATOR"
    }


@pytest.fixture
def sample_admin_data():
    """Provide sample admin data.

    Returns:
        dict: Sample admin data for testing.
    """
    return {
        "name": "Test Admin",
        "gender": "Other",
        "email": "admin@test.com",
        "phone": "9000000001",
        "address": "Admin HQ",
        "password": "admin123",
        "role": "ADMIN"
    }


@pytest.fixture
def sample_bus():
    """Provide a sample Bus object.

    Returns:
        Bus: A sample Bus instance.
    """
    from models.bus import Bus
    return Bus(
        bus_name="FastX Express",
        bus_number="PY01AB1234",
        bus_type="Sleeper AC",
        total_seats=40,
        amenities="Water Bottle,Charging Point,TV",
        operator_id=1
    )


@pytest.fixture
def sample_route_data():
    """Provide sample route data.

    Returns:
        dict: Sample route data for testing.
    """
    return {
        "bus_id": 1,
        "origin": "Puducherry",
        "destination": "Chennai",
        "journey_date": "2026-10-01",
        "departure_time": "08:00 PM",
        "arrival_time": "11:30 PM",
        "fare": 650.0
    }


@pytest.fixture
def registered_user(sample_user_data):
    """Create and return a registered user.

    Args:
        sample_user_data: Sample user data fixture.

    Returns:
        dict: Session dictionary for the registered user.
    """
    from services import auth_service
    return auth_service.register(**sample_user_data)


@pytest.fixture
def registered_operator(sample_operator_data):
    """Create and return a registered operator."""
    from services import auth_service
    return auth_service.register(**sample_operator_data, is_active=True)



@pytest.fixture
def registered_admin(sample_admin_data):
    """Create and return a registered admin.

    Args:
        sample_admin_data: Sample admin data fixture.

    Returns:
        dict: Session dictionary for the registered admin.
    """
    from services import auth_service
    return auth_service.register(**sample_admin_data)


@pytest.fixture
def seeded_bus(registered_operator):
    """Create a bus and its seats for testing.

    Args:
        registered_operator: Registered operator fixture.

    Returns:
        dict: Bus data including bus_id.
    """
    from services import bus_service
    bus_id = bus_service.add_bus(
        bus_name="Test Express",
        bus_number="TN99ZZ9999",
        bus_type="Sleeper AC",
        total_seats=16,
        amenities="Water Bottle,WiFi",
        operator_id=registered_operator['id']
    )
    return {"bus_id": bus_id, "operator": registered_operator}


@pytest.fixture
def seeded_route(seeded_bus):
    """Create a route for testing.

    Args:
        seeded_bus: Seeded bus fixture.

    Returns:
        dict: Route data including route_id.
    """
    from services import route_service
    route_id = route_service.create_route(
        bus_id=seeded_bus['bus_id'],
        origin="Puducherry",
        destination="Chennai",
        journey_date="2026-12-25",
        departure_time="08:00 PM",
        arrival_time="11:30 PM",
        fare=500.0
    )
    return {
        "route_id": route_id,
        "bus_id": seeded_bus['bus_id'],
        "fare": 500.0,
        "operator": seeded_bus['operator']
    }
