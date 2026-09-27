# Validation utility module for FastX application input verification.

import re
from datetime import datetime


def validate_name(name):
    """Validate name format."""
    if not name or not name.strip():
        return False
    return bool(re.match(r'^[A-Za-z\s]{2,50}$', name.strip()))


def validate_email(email):
    """Validate email format."""
    if not email or not email.strip():
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone):
    """Validate 10-digit Indian phone number format."""
    if not phone or not phone.strip():
        return False
    return bool(re.match(r'^[6-9]\d{9}$', phone.strip()))


def validate_password(password):
    """Validate password length."""
    if not password:
        return False
    return len(password) >= 6


_DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]


def _parse_date(date_string):
    """Parse date string against supported formats."""
    if not date_string or not date_string.strip():
        return None
    cleaned = date_string.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def validate_date(date_string):
    """Validate date string format."""
    return _parse_date(date_string) is not None


def validate_future_date(date_string):
    """Validate that date is today or in the future."""
    dt = _parse_date(date_string)
    if dt is None:
        return False
    return dt.date() >= datetime.now().date()


def validate_time(time_string):
    """Validate time format HH:MM AM/PM."""
    if not time_string or not time_string.strip():
        return False
    try:
        datetime.strptime(time_string.strip(), "%I:%M %p")
        return True
    except ValueError:
        return False


def validate_fare(fare):
    """Validate positive fare amount."""
    try:
        fare_value = float(fare)
        return fare_value > 0
    except (ValueError, TypeError):
        return False


def validate_seat_count(count):
    """Validate positive integer seat count."""
    try:
        count_value = int(count)
        return count_value > 0
    except (ValueError, TypeError):
        return False


def validate_gender(gender):
    """Validate gender option."""
    valid_genders = ['male', 'female', 'other','m','f']
    if not gender or not gender.strip():
        return False
    return gender.strip().lower() in valid_genders

