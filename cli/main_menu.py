# Main menu module for FastX application console interface.

from services import auth_service
from cli.user_menu import user_menu
from cli.operator_menu import operator_menu
from cli.admin_menu import admin_menu
from utils.helpers import print_header, print_menu, get_menu_choice
from utils.validators import validate_gender


def main_menu():
    """Display and handle main FastX menu."""
    while True:
        print_menu("FASTX - MAIN MENU", [
            "Register",
            "Login",
            "Exit"
        ])

        choice = get_menu_choice(3)

        if choice == 1:
            handle_register()
        elif choice == 2:
            handle_login()
        elif choice == 3:
            print_header("GOODBYE")
            print("  Thank you for using FastX!")
            print("  Safe travels!\n")
            break


def handle_register():
    """Handle registration flow for User and Bus Operator by role choice."""
    print_header("REGISTER NEW ACCOUNT")

    try:
        print("  Select Account Role:")
        print("    1. Passenger (User)")
        print("    2. Bus Operator")
        role_choice = get_menu_choice(2)
        role = "USER" if role_choice == 1 else "BUS_OPERATOR"
        print()

        name = input("  Enter your name       : ").strip()
        gender_input = input("  Enter gender (Male/Female/Other): ").strip()

        if not validate_gender(gender_input):
            print("\n  Invalid gender. Please enter Male, Female, or Other.\n")
            return

        gender = gender_input.capitalize()
        email = input("  Enter email           : ").strip()
        phone = input("  Enter phone (10 digit): ").strip()
        address = input("  Enter address         : ").strip()
        password = input("  Enter password (min 6): ").strip()
        confirm = input("  Confirm password      : ").strip()

        if password != confirm:
            print("\n  Passwords do not match. Please try again.\n")
            return

        result = auth_service.register(
            name=name,
            gender=gender,
            email=email,
            phone=phone,
            address=address,
            password=password,
            role=role
        )

        if result.get('is_active', True):
            print_header("REGISTRATION SUCCESSFUL")
            print(f"  Welcome, {result['name']}!")
            print(f"  Email: {result['email']}")
            print(f"  Role: {result['role']}")
            print("\n  You can now login to book tickets.\n")
        else:
            print_header("REGISTRATION PENDING ACTIVATION")
            print(f"  Welcome, {result['name']}!")
            print(f"  Email: {result['email']}")
            print(f"  Role: {result['role']}")
            print("\n  Your operator account has been registered.")
            print("  Note: Account is inactive and requires activation by Admin before logging in.\n")

    except Exception as e:
        print(f"\n  Registration failed: {str(e)}\n")


def handle_login():
    """Handle user login flow and menu routing."""
    print_header("LOGIN")

    try:
        email = input("  Enter email    : ").strip()
        password = input("  Enter password : ").strip()

        current_user = auth_service.login(email, password)

        print(f"\n  Welcome back, {current_user['name']}!")
        print(f"  Role: {current_user['role']}\n")

        if current_user['role'] == 'USER':
            user_menu(current_user)
        elif current_user['role'] == 'BUS_OPERATOR':
            operator_menu(current_user)
        elif current_user['role'] == 'ADMIN':
            admin_menu(current_user)
        else:
            print("  Unknown role. Returning to main menu.\n")

    except Exception as e:
        print(f"\n  Login failed: {str(e)}\n")

