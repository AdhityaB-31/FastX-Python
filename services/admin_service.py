# Admin service module for handling administrator management tasks.

import logging

from repositories import user_repository, booking_repository, route_repository
from decorators.decorators import log_action, require_role

logger = logging.getLogger(__name__)


@require_role("ADMIN")
@log_action
def get_all_users(current_user):
    """Get all regular users in system."""
    users = user_repository.get_all_users(role="USER")
    for user in users:
        user.pop('password', None)
    return users


@require_role("ADMIN")
@log_action
def delete_user(current_user, user_id):
    """Delete a user from the system."""
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise ValueError(f"User with ID {user_id} not found.")

    if user['role'] == 'ADMIN':
        raise ValueError("Cannot delete an admin account.")

    result = user_repository.delete_user(user_id)
    logger.info("Admin %s deleted user ID: %d", current_user['name'], user_id)
    return result


@require_role("ADMIN")
@log_action
def activate_user(current_user, user_id):
    """Activate a passenger user account."""
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise ValueError(f"User with ID {user_id} not found.")

    if user['role'] != 'USER':
        raise ValueError("The specified account is not a regular user.")

    result = user_repository.update_user(user_id, is_active=True)
    logger.info("Admin %s activated user ID: %d", current_user['name'], user_id)
    return result


@require_role("ADMIN")
@log_action
def deactivate_user(current_user, user_id):
    """Deactivate a passenger user account."""
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise ValueError(f"User with ID {user_id} not found.")

    if user['role'] != 'USER':
        raise ValueError("The specified account is not a regular user.")

    result = user_repository.update_user(user_id, is_active=False)
    logger.info("Admin %s deactivated user ID: %d", current_user['name'], user_id)
    return result


@require_role("ADMIN")
@log_action
def get_all_operators(current_user):
    """Get all bus operators in system."""
    operators = user_repository.get_all_users(role="BUS_OPERATOR")
    for operator in operators:
        operator.pop('password', None)
    return operators


@require_role("ADMIN")
@log_action
def activate_operator(current_user, operator_id):
    """Activate a bus operator account."""
    user = user_repository.find_by_id(operator_id)
    if user is None:
        raise ValueError(f"Operator with ID {operator_id} not found.")

    if user['role'] != 'BUS_OPERATOR':
        raise ValueError("The specified user is not a bus operator.")

    result = user_repository.update_user(operator_id, is_active=True)
    logger.info("Admin %s activated operator ID: %d", current_user['name'], operator_id)
    return result


@require_role("ADMIN")
@log_action
def deactivate_operator(current_user, operator_id):
    """Deactivate a bus operator account."""
    user = user_repository.find_by_id(operator_id)
    if user is None:
        raise ValueError(f"Operator with ID {operator_id} not found.")

    if user['role'] != 'BUS_OPERATOR':
        raise ValueError("The specified user is not a bus operator.")

    result = user_repository.update_user(operator_id, is_active=False)
    logger.info("Admin %s deactivated operator ID: %d", current_user['name'], operator_id)
    return result


@require_role("ADMIN")
@log_action
def delete_operator(current_user, operator_id):
    """Delete a bus operator from the system."""
    user = user_repository.find_by_id(operator_id)
    if user is None:
        raise ValueError(f"Operator with ID {operator_id} not found.")

    if user['role'] != 'BUS_OPERATOR':
        raise ValueError("The specified user is not a bus operator.")

    result = user_repository.delete_user(operator_id)
    logger.info("Admin %s deleted operator ID: %d", current_user['name'], operator_id)
    return result


@require_role("ADMIN")
@log_action
def get_all_routes(current_user):
    """Get all routes in the system."""
    return route_repository.get_all_routes()


@require_role("ADMIN")
@log_action
def delete_route(current_user, route_id):
    """Delete a route from the system."""
    result = route_repository.delete_route(route_id)
    logger.info("Admin %s deleted route ID: %d", current_user['name'], route_id)
    return result


@require_role("ADMIN")
@log_action
def get_all_bookings(current_user):
    """Get all bookings in the system."""
    return booking_repository.get_all_bookings()


@require_role("ADMIN")
@log_action
def update_booking_status(current_user, booking_id, status):
    """Update a booking status."""
    result = booking_repository.update_status(booking_id, status)
    logger.info("Admin %s updated booking %d status to: %s",
                 current_user['name'], booking_id, status)
    return result


def get_system_stats():
    """Get system-wide statistics."""
    return {
        "total_users": user_repository.get_user_count(role="USER"),
        "total_operators": user_repository.get_user_count(role="BUS_OPERATOR"),
        "total_admins": user_repository.get_user_count(role="ADMIN"),
    }

