# Admin menu module for FastX application console interface.

from services import auth_service, admin_service, route_service
from utils.helpers import (
    print_header, print_menu, print_field, print_separator,
    get_menu_choice, format_currency, format_date, confirm_action
)


def admin_menu(current_user):
    """Display and handle the admin menu."""
    while True:
        print_menu("ADMIN MENU", [
            "View Users",
            "Activate User",
            "Deactivate User",
            "Delete User",
            "View Bus Operators",
            "Activate Bus Operator",
            "Deactivate Bus Operator",
            "Delete Bus Operator",
            "View Routes",
            "Manage Routes",
            "View Bookings",
            "Manage Bookings",
            "Logout"
        ])

        choice = get_menu_choice(13)

        try:
            if choice == 1:
                handle_view_users(current_user)
            elif choice == 2:
                handle_activate_user(current_user)
            elif choice == 3:
                handle_deactivate_user(current_user)
            elif choice == 4:
                handle_delete_user(current_user)
            elif choice == 5:
                handle_view_operators(current_user)
            elif choice == 6:
                handle_activate_operator(current_user)
            elif choice == 7:
                handle_deactivate_operator(current_user)
            elif choice == 8:
                handle_delete_operator(current_user)
            elif choice == 9:
                handle_view_routes(current_user)
            elif choice == 10:
                handle_manage_routes(current_user)
            elif choice == 11:
                handle_view_bookings(current_user)
            elif choice == 12:
                handle_manage_bookings(current_user)
            elif choice == 13:
                auth_service.logout(current_user)
                print("\n  Logged out successfully.\n")
                break
        except Exception as e:
            print(f"\n  Error: {str(e)}\n")


def handle_view_users(current_user):
    """Display all registered users."""
    print_header("ALL USERS")

    users = admin_service.get_all_users(current_user)

    if not users:
        print("  No users found.\n")
        return

    print(f"  Total users: {len(users)}\n")

    for user in users:
        print_separator()
        print_field("  ID", user['id'])
        print_field("  Name", user['name'])
        print_field("  Email", user['email'])
        print_field("  Phone", user['phone'])
        print_field("  Gender", user['gender'])
        status_str = "Active" if user.get('is_active', True) else "Inactive"
        print_field("  Status", status_str)
        print_field("  Registered", user['created_at'])

    print_separator()
    print()


def handle_activate_user(current_user):
    """Handle user activation."""
    print_header("ACTIVATE USER")

    handle_view_users(current_user)

    try:
        user_id = int(input("  Enter User ID to activate (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid User ID.\n")
        return

    if user_id == 0:
        return

    if not confirm_action("  Activate this user account? (yes/no): "):
        print("\n  Activation cancelled.\n")
        return

    try:
        admin_service.activate_user(current_user, user_id)
        print(f"\n  User ID {user_id} activated successfully.\n")
    except Exception as e:
        print(f"\n  Activation failed: {str(e)}\n")


def handle_deactivate_user(current_user):
    """Handle user deactivation."""
    print_header("DEACTIVATE USER")

    handle_view_users(current_user)

    try:
        user_id = int(input("  Enter User ID to deactivate (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid User ID.\n")
        return

    if user_id == 0:
        return

    if not confirm_action("  Deactivate this user account? (yes/no): "):
        print("\n  Deactivation cancelled.\n")
        return

    try:
        admin_service.deactivate_user(current_user, user_id)
        print(f"\n  User ID {user_id} deactivated successfully.\n")
    except Exception as e:
        print(f"\n  Deactivation failed: {str(e)}\n")


def handle_delete_user(current_user):
    """Handle user deletion."""
    print_header("DELETE USER")

    handle_view_users(current_user)

    try:
        user_id = int(input("  Enter User ID to delete (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid User ID.\n")
        return

    if user_id == 0:
        return

    if not confirm_action("  Are you sure? (yes/no): "):
        print("\n  Deletion cancelled.\n")
        return

    try:
        admin_service.delete_user(current_user, user_id)
        print(f"\n  User ID {user_id} deleted successfully.\n")
    except Exception as e:
        print(f"\n  Delete failed: {str(e)}\n")


def handle_view_operators(current_user):
    """Display all bus operators."""
    print_header("ALL BUS OPERATORS")

    operators = admin_service.get_all_operators(current_user)

    if not operators:
        print("  No bus operators found.\n")
        return

    print(f"  Total operators: {len(operators)}\n")

    for op in operators:
        print_separator()
        print_field("  ID", op['id'])
        print_field("  Name", op['name'])
        print_field("  Email", op['email'])
        print_field("  Phone", op['phone'])
        print_field("  Address", op['address'])
        status_str = "Active" if op.get('is_active', True) else "Inactive (Pending Activation)"
        print_field("  Status", status_str)
        print_field("  Registered", op['created_at'])

    print_separator()
    print()


def handle_activate_operator(current_user):
    """Handle bus operator activation."""
    print_header("ACTIVATE BUS OPERATOR")

    handle_view_operators(current_user)

    try:
        operator_id = int(input("  Enter Operator ID to activate (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Operator ID.\n")
        return

    if operator_id == 0:
        return

    if not confirm_action("  Activate this operator account? (yes/no): "):
        print("\n  Activation cancelled.\n")
        return

    try:
        admin_service.activate_operator(current_user, operator_id)
        print(f"\n  Operator ID {operator_id} activated successfully.\n")
    except Exception as e:
        print(f"\n  Activation failed: {str(e)}\n")


def handle_deactivate_operator(current_user):
    """Handle bus operator deactivation."""
    print_header("DEACTIVATE BUS OPERATOR")

    handle_view_operators(current_user)

    try:
        operator_id = int(input("  Enter Operator ID to deactivate (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Operator ID.\n")
        return

    if operator_id == 0:
        return

    if not confirm_action("  Deactivate this operator account? (yes/no): "):
        print("\n  Deactivation cancelled.\n")
        return

    try:
        admin_service.deactivate_operator(current_user, operator_id)
        print(f"\n  Operator ID {operator_id} deactivated successfully.\n")
    except Exception as e:
        print(f"\n  Deactivation failed: {str(e)}\n")


def handle_delete_operator(current_user):
    """Handle operator deletion."""
    print_header("DELETE BUS OPERATOR")

    handle_view_operators(current_user)

    try:
        operator_id = int(input("  Enter Operator ID to delete (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Operator ID.\n")
        return

    if operator_id == 0:
        return

    if not confirm_action("  Are you sure? (yes/no): "):
        print("\n  Deletion cancelled.\n")
        return

    try:
        admin_service.delete_operator(current_user, operator_id)
        print(f"\n  Operator ID {operator_id} deleted successfully.\n")
    except Exception as e:
        print(f"\n  Delete failed: {str(e)}\n")


def handle_view_routes(current_user):
    """Display all routes in the system."""
    print_header("ALL ROUTES")

    routes = admin_service.get_all_routes(current_user)

    if not routes:
        print("  No routes found.\n")
        return

    print(f"  Total routes: {len(routes)}\n")

    for route in routes:
        print_separator()
        print_field("  Route ID", route['id'])
        print_field("  Bus", f"{route['bus_name']} ({route['bus_number']})")
        print_field("  Operator", route.get('operator_name', 'N/A'))
        print_field("  Route", f"{route['origin']} → {route['destination']}")
        print_field("  Date", format_date(route['journey_date']))
        print_field("  Departure", route['departure_time'])
        print_field("  Fare", format_currency(route['fare']))

    print_separator()
    print()


def handle_manage_routes(current_user):
    """Handle route deletion management."""
    print_header("MANAGE ROUTES")

    handle_view_routes(current_user)

    try:
        route_id = int(input("  Enter Route ID to delete (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Route ID.\n")
        return

    if route_id == 0:
        return

    if not confirm_action("  Delete this route? (yes/no): "):
        print("\n  Operation cancelled.\n")
        return

    try:
        admin_service.delete_route(current_user, route_id)
        print(f"\n  Route ID {route_id} deleted successfully.\n")
    except Exception as e:
        print(f"\n  Failed: {str(e)}\n")


def handle_view_bookings(current_user):
    """Display all bookings in the system."""
    print_header("ALL BOOKINGS")

    bookings = admin_service.get_all_bookings(current_user)

    if not bookings:
        print("  No bookings found.\n")
        return

    print(f"  Total bookings: {len(bookings)}\n")

    for booking in bookings:
        print_separator()
        print_field("  Booking ID", f"FXB{10001 + booking['id'] - 1}")
        print_field("  Passenger", f"{booking['passenger_name']} ({booking['passenger_email']})")
        print_field("  Bus", f"{booking['bus_name']} ({booking['bus_number']})")
        print_field("  Operator", booking.get('operator_name', 'N/A'))
        print_field("  Route", f"{booking['origin']} → {booking['destination']}")
        print_field("  Date", format_date(booking['journey_date']))
        print_field("  Amount", format_currency(booking['total_amount']))
        print_field("  Status", booking['status'])

    print_separator()
    print()


def handle_manage_bookings(current_user):
    """Handle booking status management."""
    print_header("MANAGE BOOKINGS")

    handle_view_bookings(current_user)

    try:
        booking_id = int(input("  Enter Booking ID (number, 0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Booking ID.\n")
        return

    if booking_id == 0:
        return

    print("\n  Set new status:")
    print("    1. CONFIRMED")
    print("    2. CANCELLED")
    print("    3. REFUND_PENDING")
    print("    4. REFUNDED")
    print()

    status_choice = get_menu_choice(4)

    statuses = {
        1: "CONFIRMED",
        2: "CANCELLED",
        3: "REFUND_PENDING",
        4: "REFUNDED"
    }

    new_status = statuses.get(status_choice)
    if not new_status:
        print("\n  Invalid status choice.\n")
        return

    if not confirm_action(f"  Update booking to {new_status}? (yes/no): "):
        print("\n  Operation cancelled.\n")
        return

    try:
        admin_service.update_booking_status(current_user, booking_id, new_status)
        print(f"\n  Booking {booking_id} updated to {new_status}.\n")
    except Exception as e:
        print(f"\n  Failed: {str(e)}\n")
