# Authentication service module for FastX application.

import logging

from repositories import user_repository
from utils.validators import (
    validate_name, validate_email, validate_phone, validate_password, validate_gender
)
from utils.helpers import hash_password, verify_password, get_current_datetime
from exceptions.custom_exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    AccountInactiveError,
    InvalidInputError,
)
from decorators.decorators import log_action

logger = logging.getLogger(__name__)


@log_action
def register(name, gender, email, phone, address, password, role="USER", is_active=None):
    """Register a new user or operator account."""
    if not validate_name(name):
        raise InvalidInputError("Invalid name. Use 2-50 letters and spaces only.")

    if not validate_email(email):
        raise InvalidInputError("Invalid email format.")

    if not validate_phone(phone):
        raise InvalidInputError("Invalid phone number. Must be 10 digits starting with 6-9.")

    if not validate_password(password):
        raise InvalidInputError("Password must be at least 6 characters long.")

    if user_repository.email_exists(email):
        raise DuplicateEmailError(f"An account with '{email}' already exists.")

    if is_active is None:
        is_active = (role != "BUS_OPERATOR")

    hashed_password = hash_password(password)
    created_at = get_current_datetime()

    user_id = user_repository.create_user(
        name=name.strip(),
        gender=gender,
        email=email.strip().lower(),
        phone=phone.strip(),
        address=address.strip(),
        password=hashed_password,
        role=role,
        is_active=is_active,
        created_at=created_at
    )

    logger.info("User registered: %s (ID: %d, Role: %s, Active: %s)", email, user_id, role, is_active)

    return {
        "id": user_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "role": role,
        "is_active": is_active
    }


@log_action
def login(email, password):
    """Authenticate a user with email and password."""
    if not email or not password:
        raise InvalidCredentialsError("Email and password are required.")

    user = user_repository.find_by_email(email.strip().lower())

    if user is None:
        logger.warning("Login failed - email not found: %s", email)
        raise InvalidCredentialsError("Invalid email or password.")

    if not verify_password(password, user['password']):
        logger.warning("Login failed - wrong password for: %s", email)
        raise InvalidCredentialsError("Invalid email or password.")

    if not user.get('is_active', True):
        logger.warning("Login failed - inactive account: %s", email)
        raise AccountInactiveError("Account is inactive. Please contact Administrator for activation.")

    logger.info("User logged in: %s (Role: %s)", email, user['role'])

    return {
        "id": user['id'],
        "name": user['name'],
        "email": user['email'],
        "role": user['role'],
        "is_active": user.get('is_active', True)
    }


@log_action
def logout(current_user):
    """Log out the current user."""
    if current_user:
        logger.info("User logged out: %s", current_user.get('email', 'Unknown'))
    return None


def get_user_profile(user_id):
    """Get full profile for a user."""
    user = user_repository.find_by_id(user_id)
    if user:
        profile = dict(user)
        profile.pop('password', None)
        return profile
    return None


@log_action
def update_user_profile(user_id, current_password=None, new_password=None, name=None, gender=None, phone=None, address=None, **kwargs):
    """Update user/operator profile details except email ID."""
    user = user_repository.find_by_id(user_id)
    if not user:
        raise InvalidInputError("User profile not found.")

    updates = {}

    if name is not None and name != "":
        if not validate_name(name):
            raise InvalidInputError("Invalid name. Use 2-50 letters and spaces only.")
        updates['name'] = name.strip()

    if phone is not None and phone != "":
        if not validate_phone(phone):
            raise InvalidInputError("Invalid phone number. Must be 10 digits starting with 6-9.")
        updates['phone'] = phone.strip()

    if address is not None and address != "":
        updates['address'] = address.strip()

    if gender is not None and gender != "":
        if not validate_gender(gender):
            raise InvalidInputError("Invalid gender. Please enter Male, Female, or Other.")
        updates['gender'] = gender.strip().capitalize()

    if new_password is not None and new_password != "":
        if not validate_password(new_password):
            raise InvalidInputError("Password must be at least 6 characters long.")
        if current_password:
            if not verify_password(current_password, user['password']):
                raise InvalidCredentialsError("Current password is incorrect.")
        updates['password'] = hash_password(new_password)

    if not updates:
        return get_user_profile(user_id)

    user_repository.update_user(user_id, **updates)
    logger.info("Updated profile for user ID %d: %s", user_id, list(updates.keys()))
    return get_user_profile(user_id)


