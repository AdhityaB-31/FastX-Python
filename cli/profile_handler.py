# Profile handler module for FastX application console interface.

from services import auth_service
from utils.helpers import print_header, print_field, get_menu_choice
from utils.validators import (
    validate_name, validate_phone, validate_password, validate_gender
)


def handle_view_profile(current_user):
    """Display and handle operations for the current user's or operator's profile."""
    while True:
        print_header("MY PROFILE")

        profile = auth_service.get_user_profile(current_user['id'])

        if not profile:
            print("  Profile not found.\n")
            return

        print_field("  Name", profile['name'])
        print_field("  Gender", profile['gender'])
        print_field("  Email", f"{profile['email']} (Cannot be changed)")
        print_field("  Phone", profile['phone'])
        print_field("  Address", profile['address'])
        print_field("  Role", profile['role'])
        print_field("  Registered", profile['created_at'])
        print()

        print("  Profile Options:")
        print("    1. Edit Profile Details (Name & Contact Details)")
        print("    2. Change Password")
        print("    3. Return to Main Menu")
        print()

        choice = get_menu_choice(3)

        if choice == 1:
            handle_edit_profile_details(current_user, profile)
        elif choice == 2:
            handle_change_password(current_user)
        elif choice == 3 or choice == -1:
            break


def handle_edit_profile_details(current_user, profile):
    """Handle editing profile details (Name, Phone, Address, Gender)."""
    print_header("EDIT PROFILE DETAILS")
    print("  Note: Email ID cannot be changed.")
    print("  Leave field blank to keep current value.\n")

    name = input(f"  Enter name [{profile['name']}] : ").strip()
    gender = input(f"  Enter gender [{profile['gender']}] (Male/Female/Other): ").strip()
    phone = input(f"  Enter phone [{profile['phone']}] : ").strip()
    address = input(f"  Enter address [{profile['address']}] : ").strip()

    updates = {}

    if name:
        if not validate_name(name):
            print("\n  Invalid name. Name must be 2-50 letters and spaces only.\n")
            return
        updates['name'] = name

    if gender:
        if not validate_gender(gender):
            print("\n  Invalid gender. Please enter Male, Female, or Other.\n")
            return
        updates['gender'] = gender.capitalize()

    if phone:
        if not validate_phone(phone):
            print("\n  Invalid phone. Must be 10 digits starting with 6-9.\n")
            return
        updates['phone'] = phone

    if address:
        updates['address'] = address

    if not updates:
        print("\n  No changes made.\n")
        return

    try:
        auth_service.update_user_profile(current_user['id'], **updates)
        if 'name' in updates:
            current_user['name'] = updates['name']
        print("\n  Profile details updated successfully!\n")
    except Exception as e:
        print(f"\n  Failed to update profile: {str(e)}\n")


def handle_change_password(current_user):
    """Handle changing user password."""
    print_header("CHANGE PASSWORD")

    current_password = input("  Enter current password : ").strip()
    if not current_password:
        print("\n  Current password is required.\n")
        return

    new_password = input("  Enter new password (min 6 chars) : ").strip()
    if not validate_password(new_password):
        print("\n  Password must be at least 6 characters long.\n")
        return

    confirm = input("  Confirm new password             : ").strip()
    if new_password != confirm:
        print("\n  New passwords do not match.\n")
        return

    try:
        auth_service.update_user_profile(
            current_user['id'],
            current_password=current_password,
            new_password=new_password
        )
        print("\n  Password changed successfully!\n")
    except Exception as e:
        print(f"\n  Failed to change password: {str(e)}\n")
