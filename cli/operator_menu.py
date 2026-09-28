# Bus Operator menu module for FastX application console interface.
from exceptions import InvalidJourneyDateError
from services import auth_service, route_service, bus_service, booking_service
from utils.helpers import (
    print_header, print_menu, print_field, print_separator,
    get_menu_choice, format_currency, format_date, parse_date_input,
    confirm_action
)
from utils.validators import validate_future_date, validate_fare, validate_time
from cli.profile_handler import handle_view_profile


def operator_menu(current_user):
    """Display and handle the bus operator menu."""

    while True:
        print_menu("BUS OPERATOR MENU", [
            "Add Bus Route",
            "View My Routes",
            "Update Route",
            "Delete Route",
            "Manage Seat Availability",
            "View Bookings",
            "Process Refund",
            "View Profile",
            "Logout"
        ])

        choice = get_menu_choice(9)

        try:
            if choice == 1:
                handle_add_route(current_user)
            elif choice == 2:
                handle_view_routes(current_user)
            elif choice == 3:
                handle_update_route(current_user)
            elif choice == 4:
                handle_delete_route(current_user)
            elif choice == 5:
                handle_manage_seats(current_user)
            elif choice == 6:
                handle_view_bookings(current_user)
            elif choice == 7:
                handle_process_refund(current_user)
            elif choice == 8:
                handle_view_profile(current_user)
            elif choice == 9:
                auth_service.logout(current_user)
                print("\n  Logged out successfully.\n")
                break

        except Exception as e:
            print(f"\n  Error: {str(e)}\n")


def handle_add_route(current_user):
    """Handle adding a new bus route."""
    print_header("ADD BUS ROUTE")

    # Get operator's buses
    buses = bus_service.get_operator_buses(current_user['id'])

    if not buses:
        # Create a new bus first
        print("  No buses found. Let's add a bus first.\n")
        bus_name = input("  Enter bus name       : ").strip()
        bus_number = input("  Enter bus number     : ").strip()
        bus_type = input("  Enter bus type (Seat/Sleeper AC/Semi-Sleeper/Sleeper Non-AC): ").strip()

        try:
            total_seats = int(input("  Enter total seats    : ").strip())
        except ValueError:
            print("\n  Invalid seat count.\n")
            return

        amenities = input("  Enter amenities (comma-separated): ").strip()

        print("\n  Select Schedule Type:")
        print("    1. Routine Bus (Available Every Day / Daily)")
        print("    2. Specific Date Bus")
        sched_input = input("  Enter choice (1/2, default 2): ").strip()
        is_routine = (sched_input == "1")

        try:
            bus_id = bus_service.add_bus(
                bus_name, bus_number, bus_type, total_seats,
                amenities, current_user['id'], is_routine=is_routine
            )
            routine_label = "Routine Bus (Daily)" if is_routine else "Specific Date Bus"
            print(f"\n  Bus '{bus_name}' ({routine_label}) added successfully! (ID: {bus_id})\n")
        except Exception as e:
            print(f"\n  Failed to add bus: {str(e)}\n")
            return
    else:
        # Show existing buses
        print("  Your buses:\n")
        for bus in buses:
            sched_str = "Routine Daily" if bus.get('is_routine') else "Specific Date"
            print(f"    ID: {bus['id']} | {bus['bus_name']} ({bus['bus_number']}) "
                  f"- {bus['bus_type']} [{sched_str}]")

        print()

        try:
            bus_id = int(input("  Enter Bus ID for this route (or 0 to add new bus): ").strip())
        except ValueError:
            print("\n  Invalid input.\n")
            return

        if bus_id == 0:
            # Add new bus
            bus_name = input("  Enter bus name       : ").strip()
            bus_number = input("  Enter bus number     : ").strip()
            bus_type = input("  Enter bus type (Seat/Sleeper AC/Semi-Sleeper/Sleeper Non-AC): ").strip()

            try:
                total_seats = int(input("  Enter total seats    : ").strip())
            except ValueError:
                print("\n  Invalid seat count.\n")
                return

            amenities = input("  Enter amenities (comma-separated): ").strip()

            print("\n  Select Schedule Type:")
            print("    1. Routine Bus (Available Every Day / Daily)")
            print("    2. Specific Date Bus")
            sched_input = input("  Enter choice (1/2, default 2): ").strip()
            is_routine = (sched_input == "1")

            try:
                bus_id = bus_service.add_bus(
                    bus_name, bus_number, bus_type, total_seats,
                    amenities, current_user['id'], is_routine=is_routine
                )
                routine_label = "Routine Bus (Daily)" if is_routine else "Specific Date Bus"
                print(f"\n  Bus added ({routine_label})! (ID: {bus_id})\n")
            except Exception as e:
                print(f"\n  Failed to add bus: {str(e)}\n")
                return

    # Add route details
    print("  Route Details:")
    origin = input("  Enter origin         : ").strip()
    destination = input("  Enter destination    : ").strip()
    journey_date = input("  Enter journey date (DD-MM-YYYY): ").strip()

    if not validate_future_date(journey_date):
        raise InvalidJourneyDateError("Journey Date should be in Future")

    departure_time = input("  Enter departure time (e.g., 08:00 PM): ").strip()
    arrival_time = input("  Enter arrival time (e.g., 11:30 PM): ").strip()
    fare_input = input("  Enter fare per seat  : ").strip()

    if not validate_fare(fare_input):
        print("\n  Invalid fare amount.\n")
        return

    fare = float(fare_input)
    db_date = parse_date_input(journey_date)

    try:
        route_id = route_service.create_route(
            bus_id, origin, destination, db_date,
            departure_time, arrival_time, fare
        )
        print(f"\n  Route added successfully! (ID: {route_id})")
        print(f"  {origin} → {destination} on {journey_date}\n")
    except Exception as e:
        print(f"\n  Failed to add route: {str(e)}\n")


def handle_view_routes(current_user):
    """View all routes for the current operator."""
    print_header("MY ROUTES")

    routes = route_service.get_operator_routes(current_user['id'])

    if not routes:
        print("  No routes found.\n")
        return

    for i, route in enumerate(routes, 1):
        print_separator()
        print(f"  Route #{i} (ID: {route['id']})")
        print_separator("-", 50)
        print_field("  Bus", f"{route['bus_name']} ({route['bus_number']})")
        print_field("  Operator", route.get('operator_name', 'N/A'))
        print_field("  Type", route['bus_type'])
        sched_type_str = "Routine Bus (Available Daily)" if route.get('is_routine') else "Specific Date Bus"
        print_field("  Schedule Type", sched_type_str)
        print_field("  Origin", route['origin'])
        print_field("  Destination", route['destination'])
        date_str = "Every Day (Routine)" if route.get('is_routine') else format_date(route['journey_date'])
        print_field("  Journey Date", date_str)
        print_field("  Departure", route['departure_time'])
        print_field("  Arrival", route['arrival_time'])
        print_field("  Fare", format_currency(route['fare']))

        available = bus_service.get_available_seats(route['bus_id'])
        print_field("  Available Seats", len(available))

    print_separator()
    print()


def handle_update_route(current_user):
    """Handle updating a route's information."""
    print_header("UPDATE ROUTE")

    handle_view_routes(current_user)

    try:
        route_id = int(input("  Enter Route ID to update (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Route ID.\n")
        return

    if route_id == 0:
        return

    print("\n  Leave blank to keep current value.\n")

    updates = {}

    origin = input("  New origin       : ").strip()
    if origin:
        updates['origin'] = origin

    destination = input("  New destination  : ").strip()
    if destination:
        updates['destination'] = destination

    date_input = input("  New date (DD-MM-YYYY): ").strip()
    if date_input:
        if validate_future_date(date_input):
            updates['journey_date'] = parse_date_input(date_input)
        else:
            print("\n  Invalid date. Skipping date update.\n")

    departure = input("  New departure time: ").strip()
    if departure:
        updates['departure_time'] = departure

    arrival = input("  New arrival time  : ").strip()
    if arrival:
        updates['arrival_time'] = arrival

    fare_input = input("  New fare          : ").strip()
    if fare_input:
        if validate_fare(fare_input):
            updates['fare'] = float(fare_input)
        else:
            print("\n  Invalid fare. Skipping fare update.\n")

    if not updates:
        print("\n  No changes made.\n")
        return

    try:
        route_service.update_route(route_id, **updates)
        print("\n  Route updated successfully!\n")
    except Exception as e:
        print(f"\n  Update failed: {str(e)}\n")


def handle_delete_route(current_user):
    """Handle deleting a route."""
    print_header("DELETE ROUTE")

    handle_view_routes(current_user)

    try:
        route_id = int(input("  Enter Route ID to delete (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Route ID.\n")
        return

    if route_id == 0:
        return

    if not confirm_action("  Are you sure? (yes/no): "):
        print("\n  Deletion cancelled.\n")
        return

    try:
        route_service.delete_route(route_id)
        print("\n  Route deleted successfully!\n")
    except Exception as e:
        print(f"\n  Delete failed: {str(e)}\n")


def handle_manage_seats(current_user):
    """Handle seat availability management."""
    print_header("MANAGE SEAT AVAILABILITY")

    buses = bus_service.get_operator_buses(current_user['id'])

    if not buses:
        print("  No buses found.\n")
        return

    print("  Your buses:\n")
    for bus in buses:
        available = bus_service.get_available_seats(bus['id'])
        total = bus['total_seats']
        print(f"    ID: {bus['id']} | {bus['bus_name']} "
              f"({len(available)}/{total} available)")

    print()

    try:
        bus_id = int(input("  Enter Bus ID (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Bus ID.\n")
        return

    if bus_id == 0:
        return

    bus_service.display_seats_with_iterator(bus_id)

    print("  Options:")
    print("    1. Reset all seats to AVAILABLE")
    print("    2. Return to menu")
    print()

    sub_choice = get_menu_choice(2)

    if sub_choice == 1:
        if confirm_action("  Reset all seats? (yes/no): "):
            count = bus_service.reset_all_seats(bus_id)
            print(f"\n  {count} seats reset to AVAILABLE.\n")
    else:
        return


def handle_view_bookings(current_user):
    """View all bookings for the operator's routes."""
    print_header("BOOKINGS ON MY ROUTES")

    try:
        bookings = booking_service.get_operator_bookings(current_user)

        if not bookings:
            print("  No bookings found.\n")
            return

        for booking in bookings:
            print_separator()
            print_field("  Booking ID", f"FXB{10001 + booking['id'] - 1}")
            print_field("  Passenger", f"{booking['passenger_name']} ({booking['passenger_email']})")
            print_field("  Route", f"{booking['origin']} → {booking['destination']}")
            print_field("  Date", format_date(booking['journey_date']))
            print_field("  Bus", f"{booking['bus_name']} ({booking['bus_number']})")
            print_field("  Operator", booking.get('operator_name', 'N/A'))
            print_field("  Amount", format_currency(booking['total_amount']))
            print_field("  Status", booking['status'])

        print_separator()
        print()

    except Exception as e:
        print(f"\n  Error: {str(e)}\n")


def handle_process_refund(current_user):
    """Handle refund processing for a cancelled booking."""
    print_header("PROCESS REFUND")

    try:
        booking_id = int(input("  Enter Booking ID (number, 0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Booking ID.\n")
        return

    if booking_id == 0:
        return

    try:
        result = booking_service.process_operator_refund(current_user, booking_id)

        print("\n  Refund processed successfully!\n")
        print_field("  Booking ID", result['booking_display_id'])
        print_field("  Original Transaction", result['original_transaction'])
        print_field("  Refund Amount", format_currency(result['refund_amount']))
        print_field("  Refund Status", result['refund_status'])
        print()

    except Exception as e:
        print(f"\n  Refund failed: {str(e)}\n")
