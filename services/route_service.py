# Route service module for route searching and management operations.

import logging

from repositories import route_repository, seat_repository
from decorators.decorators import log_action
from exceptions.custom_exceptions import RouteNotFoundError

logger = logging.getLogger(__name__)


@log_action
def search_routes(**filters):
    """Search for routes using keyword filters."""
    routes = route_repository.search_routes(**filters)

    sorted_routes = sorted(
        routes,
        key=lambda route: route["fare"]
    )

    return sorted_routes


def get_route_details(route_id):
    """Get detailed information about a specific route."""
    route = route_repository.find_by_id(route_id)
    if route is None:
        raise RouteNotFoundError(f"Route with ID {route_id} not found.")
    return route


def get_all_routes():
    """Get all available routes with formatted display strings."""
    routes = route_repository.get_all_routes()

    routes_with_display = list(map(
        lambda r: {**r, 'display_text': f"{r['origin']} → {r['destination']} ({r['journey_date']})"},
        routes
    ))

    return routes_with_display


def get_operator_routes(operator_id):
    """Get all routes for a specific operator."""
    return route_repository.get_routes_by_operator(operator_id)


@log_action
def create_route(bus_id, origin, destination, journey_date,
                 departure_time, arrival_time, fare):
    """Create a new route."""
    route_id = route_repository.create_route(
        bus_id, origin, destination, journey_date,
        departure_time, arrival_time, fare
    )
    return route_id


@log_action
def update_route(route_id, **kwargs):
    """Update route information."""
    route = route_repository.find_by_id(route_id)
    if route is None:
        raise RouteNotFoundError(f"Route with ID {route_id} not found.")

    return route_repository.update_route(route_id, **kwargs)


@log_action
def delete_route(route_id):
    """Delete a route."""
    route = route_repository.find_by_id(route_id)
    if route is None:
        raise RouteNotFoundError(f"Route with ID {route_id} not found.")

    return route_repository.delete_route(route_id)


def filter_routes_by_availability(routes, min_seats=1):
    """Filter routes that have minimum available seats."""
    def has_available_seats(route):
        """Check if route's bus has available seats."""
        count = seat_repository.count_available_seats(route['bus_id'])
        return count >= min_seats

    return list(filter(has_available_seats, routes))

