# Helper utility module for FastX application formatting, encryption, and console output.

import hashlib
from datetime import datetime


def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify password against its hash."""
    return hash_password(password) == hashed


def format_currency(amount):
    """Format number as Indian Rupee currency."""
    amount = float(amount)
    return f"Rs. {amount:.0f}" if amount == int(amount) else f"Rs. {amount:.2f}"


def format_date(date_string):
    """Convert date from DB format YYYY-MM-DD to display format DD-MM-YYYY."""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return date_string


def parse_date_input(date_string):
    """Convert user input date string to DB format YYYY-MM-DD."""
    if not date_string or not date_string.strip():
        return date_string

    cleaned = date_string.strip()
    formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_string


def print_header(title):
    """Print formatted section header."""
    width = max(len(title) + 10, 50)
    print()
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)
    print()


def print_separator(char="-", length=50):
    """Print separator line."""
    print(char * length)


def print_field(label, value, label_width=18):
    """Print formatted key-value field."""
    print(f"{label:<{label_width}}: {value}")


def print_menu(title, options):
    """Print formatted menu with numbered options."""
    print_header(title)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print()


def get_menu_choice(max_choice):
    """Get validated menu choice from user."""
    try:
        choice = int(input("Enter your choice: ").strip())
        if 1 <= choice <= max_choice:
            return choice
        else:
            print(f"Please enter a number between 1 and {max_choice}.")
            return -1
    except ValueError:
        print("Invalid input. Please enter a number.")
        return -1


def confirm_action(message="Are you sure? (yes/no): "):
    """Ask user for yes/no confirmation."""
    response = input(message).strip().lower()
    return response in ('yes', 'y')


def get_current_datetime():
    """Get current datetime string YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date():
    """Get current date string YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

