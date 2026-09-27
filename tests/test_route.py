"""
Tests for Route model and route service.

Tests route creation, searching with **kwargs,
sorting with lambda, and route CRUD operations.
"""

import pytest

from models.route import Route
from services import route_service
from exceptions.custom_exceptions import RouteNotFoundError


class TestRouteModel:
    """Test group for Route model."""

    def test_route_creation(self):
        """Test creating a Route with default fare."""
        route = Route(
            bus_id=1,
            origin="Puducherry",
            destination="Chennai",
            journey_date="2026-10-01",
            departure_time="08:00 PM",
            arrival_time="11:30 PM"
        )
        assert route.origin == "Puducherry"
        assert route.destination == "Chennai"
        assert route.fare == 0.0

    def test_route_creation_with_fare(self):
        """Test creating a Route with specified fare."""
        route = Route(
            bus_id=1,
            origin="Chennai",
            destination="Bangalore",
            journey_date="2026-10-01",
            departure_time="10:00 PM",
            arrival_time="06:00 AM",
            fare=850.0
        )
        assert route.fare == 850.0

    def test_route_negative_fare_raises(self):
        """Test that negative fare raises ValueError."""
        route = Route(bus_id=1, origin="A", destination="B",
                      journey_date="2026-01-01",
                      departure_time="08:00 AM",
                      arrival_time="10:00 AM",
                      fare=100)
        with pytest.raises(ValueError, match="cannot be negative"):
            route.fare = -50

    def test_route_str(self):
        """Test Route string representation."""
        route = Route(bus_id=1, origin="Puducherry",
                      destination="Chennai",
                      journey_date="2026-10-01",
                      departure_time="08:00 PM",
                      arrival_time="11:30 PM",
                      fare=650)
        result = str(route)
        assert "Puducherry" in result
        assert "Chennai" in result


class TestRouteService:
    """Test group for route service operations."""

    def test_create_route(self, seeded_bus):
        """Test creating a route through the service."""
        route_id = route_service.create_route(
            bus_id=seeded_bus['bus_id'],
            origin="Chennai",
            destination="Madurai",
            journey_date="2026-11-15",
            departure_time="09:00 PM",
            arrival_time="04:00 AM",
            fare=750.0
        )
        assert route_id is not None
        assert route_id > 0

    def test_get_route_details(self, seeded_route):
        """Test getting route details."""
        route = route_service.get_route_details(seeded_route['route_id'])
        assert route['origin'] == "Puducherry"
        assert route['destination'] == "Chennai"
        assert route['fare'] == 500.0

    def test_get_route_not_found(self):
        """Test getting a non-existent route raises error."""
        with pytest.raises(RouteNotFoundError):
            route_service.get_route_details(99999)

    def test_search_routes_with_kwargs(self, seeded_route):
        """Test searching routes with **kwargs."""
        results = route_service.search_routes(
            origin="Puducherry",
            destination="Chennai"
        )
        assert len(results) >= 1
        assert results[0]['origin'] == "Puducherry"

    def test_search_routes_no_results(self):
        """Test search with no matching routes."""
        results = route_service.search_routes(
            origin="Nonexistent",
            destination="Nowhere"
        )
        assert len(results) == 0

    def test_search_routes_sorted_by_fare(self, seeded_bus):
        """Test that search results are sorted by fare (lambda)."""
        # Create two routes with different fares
        route_service.create_route(seeded_bus['bus_id'], "A", "B",
                                   "2026-12-01", "08:00 AM", "12:00 PM", 900.0)
        route_service.create_route(seeded_bus['bus_id'], "A", "B",
                                   "2026-12-01", "10:00 AM", "02:00 PM", 500.0)

        results = route_service.search_routes(origin="A", destination="B")
        assert len(results) == 2
        # Should be sorted ascending by fare
        assert results[0]['fare'] <= results[1]['fare']

    def test_update_route(self, seeded_route):
        """Test updating a route."""
        result = route_service.update_route(
            seeded_route['route_id'],
            fare=600.0,
            origin="New Origin"
        )
        assert result is True

        updated = route_service.get_route_details(seeded_route['route_id'])
        assert updated['fare'] == 600.0
        assert updated['origin'] == "New Origin"

    def test_delete_route(self, seeded_route):
        """Test deleting a route."""
        result = route_service.delete_route(seeded_route['route_id'])
        assert result is True

        with pytest.raises(RouteNotFoundError):
            route_service.get_route_details(seeded_route['route_id'])

    def test_search_routes_with_empty_date(self, registered_operator):
        """Test searching routes with an empty date filter returns all dates."""
        from services import bus_service
        bus1_id = bus_service.add_bus("Routine Bus", "TN99RT0001", "Seat", 30, "", registered_operator['id'], is_routine=True)
        bus2_id = bus_service.add_bus("Specific Date Bus", "TN99ST0002", "Seat", 30, "", registered_operator['id'], is_routine=False)

        route_service.create_route(bus1_id, "Chennai", "Salem", "2026-10-01", "08:00 AM", "12:00 PM", 400.0)
        route_service.create_route(bus2_id, "Chennai", "Salem", "2026-10-15", "09:00 AM", "01:00 PM", 450.0)

        # Search with journey_date=None (empty date filter)
        results = route_service.search_routes(origin="Chennai", destination="Salem", journey_date=None)
        assert len(results) == 2

    def test_search_routes_routine_bus_matches_any_date(self, registered_operator):
        """Test routine buses are available on any searched journey date."""
        from services import bus_service
        bus1_id = bus_service.add_bus("Daily Routine", "TN99RT0003", "Seat", 30, "", registered_operator['id'], is_routine=True)
        bus2_id = bus_service.add_bus("Specific Date", "TN99ST0004", "Seat", 30, "", registered_operator['id'], is_routine=False)

        route_service.create_route(bus1_id, "Trichy", "Madurai", "2026-10-01", "08:00 AM", "10:00 AM", 300.0)
        route_service.create_route(bus2_id, "Trichy", "Madurai", "2026-10-05", "10:00 AM", "12:00 PM", 350.0)

        # Search for 2026-10-20 (a date neither route was specifically scheduled for)
        results = route_service.search_routes(origin="Trichy", destination="Madurai", journey_date="2026-10-20")
        assert len(results) == 1
        assert results[0]['bus_number'] == "TN99RT0003"
        assert results[0]['is_routine'] == 1 or results[0]['is_routine'] is True
