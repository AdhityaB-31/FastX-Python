# Custom decorators module for logging and role-based authorization.

import logging
from functools import wraps

from exceptions.custom_exceptions import UnauthorizedActionError

logger = logging.getLogger(__name__)


def log_action(function):
    """Decorator that logs the execution of a function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        logger.info("Executing: %s", function.__name__)
        try:
            result = function(*args, **kwargs)
            logger.info("Completed: %s", function.__name__)
            return result
        except Exception as e:
            logger.error("Error in %s: %s", function.__name__, str(e))
            raise

    return wrapper


def require_role(required_role):
    """Parameterized decorator that enforces role-based authorization."""

    def decorator(function):

        @wraps(function)
        def wrapper(current_user, *args, **kwargs):
            if current_user is None:
                raise UnauthorizedActionError("No user is currently logged in.")

            user_role = current_user.get("role", "")

            if user_role != required_role:
                raise UnauthorizedActionError(
                    f"Access denied. Required role: {required_role}, "
                    f"your role: {user_role}."
                )

            return function(current_user, *args, **kwargs)

        return wrapper

    return decorator

