# User menu module for FastX application console interface.
from exceptions import InvalidJourneyDateError
from services import auth_service, route_service, bus_service, booking_service
from utils.helpers import (
    print_header, print_menu, print_field, print_separator,
    get_menu_choice, format_currency, format_date, confirm_action
)
from utils.validators import validate_future_date
from models.person import Person
from models.user import User
from models.operator import BusOperator
from models.admin import Admin
from cli.profile_handler import handle_view_profile


def user_menu(current_user):
    """Display and handle the passenger menu."""

    # Demonstrate polymorphism with get_dashboard()
    people = [
        User("Passenger"),
        BusOperator("Operator"),
        Admin("Administrator")
    ]
    print(f"\n  Dashboard: ", end="")
    # Polymorphism - same method, different behavior
    for person in people:
        if person.get_role() == "USER":
            print(person.get_dashboard())
            break

    while True:
        print_menu("FASTX USER MENU", [
            "Search Bus",
            "View Available Routes",
            "Select Seats",
            "Book Ticket",
            "View Booking",
            "Booking History",
            "Cancel Booking",
            "Request Refund",
            "View Profile",
            "Logout"
        ])

        choice = get_menu_choice(10)

        try:
            if choice == 1:
                handle_search_bus(current_user)
            elif choice == 2:
                handle_view_routes(current_user)
            elif choice == 3:
                handle_select_seats(current_user)
            elif choice == 4:
                handle_book_ticket(current_user)
            elif choice == 5:
                handle_view_booking()
            elif choice == 6:
                handle_booking_history(current_user)
            elif choice == 7:
                handle_cancel_booking(current_user)
            elif choice == 8:
                handle_request_refund(current_user)
            elif choice == 9:
                handle_view_profile(current_user)
            elif choice == 10:
                auth_service.logout(current_user)
                print("\n  Logged out successfully.\n")
                break
        except Exception as e:
            print(f"\n  Error: {str(e)}\n")


def handle_search_bus(current_user=None):
    """Handle bus search by origin, destination, and journey date."""
    print_header("SEARCH BUS")

    origin = input("  Enter origin       : ").strip()
    destination = input("  Enter destination  : ").strip()
    journey_date = input("  Enter journey date (DD-MM-YYYY, or press Enter for all dates): ").strip()

    db_date = None
    if journey_date:
        if not validate_future_date(journey_date):
           raise InvalidJourneyDateError("\n  Invalid or past date. Please enter a valid future date or leave empty for all dates.\n")
        from utils.helpers import parse_date_input
        db_date = parse_date_input(journey_date)

    # Use **kwargs for search
    routes = route_service.search_routes(
        origin=origin,
        destination=destination,
        journey_date=db_date
    )

    if not routes:
        print("\n  No buses found for the given criteria.\n")
        return

    print_header("SEARCH RESULTS")
    print(f"  Found {len(routes)} bus(es):\n")

    for i, route in enumerate(routes, 1):
        print_separator()
        print(f"  Route #{i} (ID: {route['id']})")
        print_separator("-", 40)
        print_field("  Bus Name", route['bus_name'])
        print_field("  Operator", route.get('operator_name', 'N/A'))
        print_field("  Bus Number", route['bus_number'])
        print_field("  Bus Type", route['bus_type'])
        sched_type_str = "Daily (Routine Bus)" if route.get('is_routine') else format_date(route['journey_date'])
        print_field("  Schedule / Date", sched_type_str)
        print_field("  Origin", route['origin'])
        print_field("  Destination", route['destination'])
        print_field("  Departure", route['departure_time'])
        print_field("  Arrival", route['arrival_time'])
        print_field("  Fare", format_currency(route['fare']))

        # Get available seat count
        r_date = route['journey_date'] if not route.get('is_routine') else db_date
        available = bus_service.get_available_seats(route['bus_id'], journey_date=r_date)
        print_field("  Available Seats", len(available))

        amenities = route.get('amenities', '')
        if amenities:
            print_field("  Amenities", amenities)

    print_separator()
    print()

    print("  Do you want to proceed with booking?")
    print("  1. Proceed to Book Ticket")
    print("  0. Return to Main Menu")

    choice = input("\n  Enter choice (1/0 or press 0 to enter menu): ").strip()
    if choice == "1":
        handle_book_ticket(current_user, default_journey_date=db_date)
    elif choice.isdigit() and int(choice) > 0:
        handle_book_ticket(current_user, route_id=int(choice), default_journey_date=db_date)


def handle_view_routes(current_user=None):
    """Display all available routes."""
    print_header("AVAILABLE ROUTES")

    routes = route_service.get_all_routes()

    if not routes:
        print("  No routes available.\n")
        return

    for i, route in enumerate(routes, 1):
        print_separator("-",40)
        print(f"  Route #{i} (ID: {route['id']})")
        print_separator("-", 40)
        print_field("  Bus Name", route['bus_name'])
        print_field("  Operator", route.get('operator_name', 'N/A'))
        print_field("  Origin", route['origin'])
        print_field("  Destination", route['destination'])
        sched_type_str = "Daily (Routine Bus)" if route.get('is_routine') else format_date(route['journey_date'])
        print_field("  Schedule / Date", sched_type_str)
        print_field("  Departure", route['departure_time'])
        print_field("  Fare", format_currency(route['fare']))

    print_separator("-",40)
    print()

    print("  Do you want to proceed with booking?")
    print("  1. Proceed to Book Ticket")
    print("  0. Return to Main Menu")

    choice = input("\n  Enter choice (1/0 or press 0 to enter menu): ").strip()
    if choice == "1":
        handle_book_ticket(current_user)
    elif choice.isdigit() and int(choice) > 0:
        handle_book_ticket(current_user, route_id=int(choice))


def handle_select_seats(current_user=None):
    """Display seat layout for a selected route."""
    print_header("SELECT SEATS")

    try:
        route_id = int(input("  Enter Route ID (0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Route ID.\n")
        return

    if route_id == 0:
        return

    try:
        route = route_service.get_route_details(route_id)
    except Exception as e:
        print(f"\n  {str(e)}\n")
        return

    print(f"\n  Bus: {route['bus_name']} ({route['bus_number']})")
    print(f"  Operator: {route.get('operator_name', 'N/A')}")
    print(f"  Route: {route['origin']} → {route['destination']}")
    print(f"  Fare: {format_currency(route['fare'])}")

    s_date = route['journey_date']
    if route.get('is_routine'):
        print("  Schedule: Daily (Routine Bus)")
        d_inp = input("  Enter journey date (DD-MM-YYYY, or press Enter for today): ").strip()
        if d_inp and validate_future_date(d_inp):
            from utils.helpers import parse_date_input
            s_date = parse_date_input(d_inp)
        else:
            from utils.helpers import get_current_date
            s_date = get_current_date()

    # Display seats using SeatIterator
    bus_service.display_seats_with_iterator(route['bus_id'], journey_date=s_date)

    print_separator()
    print()

    print("  Do you want to proceed with booking?")
    print("  1. Proceed to Book Ticket")
    print("  0. Return to Main Menu")

    choice = input("\n  Enter choice (1/0 or press 0 to enter menu): ").strip()
    if choice == "1":
        handle_book_ticket(current_user, route_id=route_id)


def handle_book_ticket(current_user=None, route_id=None, default_journey_date=None):
    """Handle the full ticket booking flow.

    Args:
        current_user: The current user session dictionary.
        route_id: Optional pre-selected route ID.
        default_journey_date: Optional default journey date (YYYY-MM-DD format).
    """
    print_header("BOOK TICKET")

    if route_id is None:
        try:
            route_id = int(input("  Enter Route ID (0 to go back): ").strip())
        except ValueError:
            print("\n  Invalid Route ID.\n")
            return

        if route_id == 0:
            return

    try:
        route = route_service.get_route_details(route_id)
    except Exception as e:
        print(f"\n  {str(e)}\n")
        return

    # Show route info
    print(f"\n  Bus: {route['bus_name']} ({route['bus_number']})")
    print(f"  Operator: {route.get('operator_name', 'N/A')}")
    print(f"  Route: {route['origin']} → {route['destination']}")

    selected_journey_date = None
    if route.get('is_routine'):
        print("  Schedule: Daily (Routine Bus)")
        while True:
            if default_journey_date:
                prompt_msg = f"  Enter journey date (DD-MM-YYYY, press Enter to use {format_date(default_journey_date)}): "
            else:
                prompt_msg = "  Enter journey date (DD-MM-YYYY): "

            date_input = input(prompt_msg).strip()
            if not date_input:
                if default_journey_date:
                    selected_journey_date = default_journey_date
                    break
                else:
                    print("  Journey date is required for daily routine buses. Please try again.")
                    continue
            if not validate_future_date(date_input):
                print("  Invalid or past date. Please enter a valid future date (DD-MM-YYYY).")
                continue
            from utils.helpers import parse_date_input
            selected_journey_date = parse_date_input(date_input)
            break
    else:
        selected_journey_date = route['journey_date']
        print(f"  Date: {format_date(selected_journey_date)}")

    print(f"  Fare per seat: {format_currency(route['fare'])}")

    # Display seats
    bus_service.display_seats_with_iterator(route['bus_id'], journey_date=selected_journey_date)

    # Get seat selection
    seats_input = input("  Enter seats (comma-separated, e.g., A1,A3,B2): ").strip()
    if not seats_input:
        print("\n  No seats selected.\n")
        return

    seat_numbers = [s.strip().upper() for s in seats_input.split(",") if s.strip()]

    if not seat_numbers:
        print("\n  No valid seats entered.\n")
        return

    # Check for invalid or booked seats before proceeding
    try:
        found_seats = bus_service.find_seats_by_numbers(route['bus_id'], seat_numbers, journey_date=selected_journey_date)
        found_map = {s['seat_number']: s for s in found_seats}

        missing = [sn for sn in seat_numbers if sn not in found_map]
        if missing:
            print(f"\n  Invalid seat(s): {', '.join(missing)}. Please check available seats.\n")
            return

        booked = [sn for sn in seat_numbers if found_map[sn]['status'] != 'AVAILABLE']
        if booked:
            print(f"\n  Seat(s) already booked and not selectable: {', '.join(booked)}. Please select available seats.\n")
            return
    except Exception:
        pass

    # Show fare calculation
    fare_per_seat = route['fare']
    total_fare = booking_service.calculate_fare(fare_per_seat, len(seat_numbers))

    print(f"\n  Fare per seat  : {format_currency(fare_per_seat)}")
    print(f"  Seats selected : {len(seat_numbers)}")
    print(f"  Total Fare     : {format_currency(total_fare)}")

    if not confirm_action("\n  Confirm booking? (yes/no): "):
        print("\n  Booking cancelled.\n")
        return

    # Process booking
    try:
        # Payment display
        print_header("PAYMENT")
        print(f"  Seats          : {', '.join(seat_numbers)}")
        print(f"  Total Amount   : {format_currency(total_fare)}")
        print(f"  Payment Method : DUMMY_PAYMENT")
        print("\n  Processing payment...\n")

        confirmation = booking_service.book_ticket(
            current_user, route_id, seat_numbers, journey_date=selected_journey_date
        )

        # Booking confirmation
        print("=" * 50)
        print(f"{'BOOKING CONFIRMED':^50}")
        print("=" * 50)
        print()
        print_field("  Booking ID", confirmation['booking_display_id'])
        print_field("  Passenger", confirmation['passenger_name'])
        print_field("  Bus", confirmation['bus_name'])
        print_field("  Operator", confirmation.get('operator_name', 'N/A'))
        print_field("  Origin", confirmation['origin'])
        print_field("  Destination", confirmation['destination'])
        print_field("  Journey Date", format_date(confirmation['journey_date']))
        print_field("  Seats", confirmation['seats'])
        print_field("  Total Amount", format_currency(confirmation['total_amount']))
        print()
        print_field("  Transaction ID", confirmation['transaction_id'])
        print_field("  Payment Status", confirmation['payment_status'])
        print_field("  Booking Status", confirmation['booking_status'])
        print()
        print("=" * 50)
        print()

    except Exception as e:
        print(f"\n  Booking failed: {str(e)}\n")


def handle_view_booking():
    """View details of a specific booking."""
    print_header("VIEW BOOKING")

    try:
        booking_id = int(input("  Enter Booking ID (number, 0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Booking ID.\n")
        return

    if booking_id == 0:
        return

    try:
        booking = booking_service.get_booking_details(booking_id)

        print_separator()
        print_field("  Booking ID", f"FXB{10001 + booking['id'] - 1}")
        print_field("  Passenger", booking['passenger_name'])
        print_field("  Bus", f"{booking['bus_name']} ({booking['bus_number']})")
        print_field("  Operator", booking.get('operator_name', 'N/A'))
        print_field("  Route", f"{booking['origin']} → {booking['destination']}")
        print_field("  Journey Date", format_date(booking['journey_date']))
        print_field("  Departure", booking['departure_time'])
        print_field("  Seats", booking['seat_numbers'])
        print_field("  Total Amount", format_currency(booking['total_amount']))
        print_field("  Booking Status", booking['status'])

        if booking.get('payment'):
            print_field("  Transaction ID", booking['payment']['transaction_id'])
            print_field("  Payment Status", booking['payment']['status'])

            if booking['payment'].get('refund_amount', 0) > 0:
                print_field("  Refund Amount",
                            format_currency(booking['payment']['refund_amount']))

        print_separator()
        print()

    except Exception as e:
        print(f"\n  {str(e)}\n")


def handle_booking_history(current_user):
    """Display booking history for the current user."""
    print_header("BOOKING HISTORY")

    history = booking_service.get_booking_history(current_user['id'])
    bookings = history['bookings']

    if not bookings:
        print("  No bookings found.\n")
        return

    print(f"  Total bookings: {history['booking_count']}")
    print(f"  Total spent   : {format_currency(history['total_spent'])}\n")

    for booking in bookings:
        print_separator()
        print_field("  Booking ID", f"FXB{10001 + booking['id'] - 1}")
        print_field("  Bus", f"{booking['bus_name']} ({booking['bus_number']})")
        print_field("  Operator", booking.get('operator_name', 'N/A'))
        print_field("  Route", f"{booking['origin']} → {booking['destination']}")
        print_field("  Date", format_date(booking['journey_date']))
        print_field("  Seats", booking.get('seat_numbers', 'N/A'))
        print_field("  Amount", format_currency(booking['total_amount']))
        print_field("  Status", booking['status'])

    print_separator()
    print()


def handle_cancel_booking(current_user):
    """Handle booking cancellation."""
    print_header("CANCEL BOOKING")

    try:
        booking_id = int(input("  Enter Booking ID (number, 0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Booking ID.\n")
        return

    if booking_id == 0:
        return

    if not confirm_action("  Are you sure you want to cancel? (yes/no): "):
        print("\n  Cancellation aborted.\n")
        return

    try:
        result = booking_service.cancel_booking(current_user, booking_id)

        print("\n  Booking cancelled successfully!")
        print_field("  Booking ID", result['booking_display_id'])
        print_field("  Status", result['status'])
        print_field("  Amount", format_currency(result['total_amount']))
        print("\n  You can now request a refund from the Refund menu.\n")

    except Exception as e:
        print(f"\n  Cancellation failed: {str(e)}\n")


def handle_request_refund(current_user):
    """Handle refund request for a cancelled booking."""
    print_header("REQUEST REFUND")

    try:
        booking_id = int(input("  Enter Booking ID (number, 0 to go back): ").strip())
    except ValueError:
        print("\n  Invalid Booking ID.\n")
        return

    if booking_id == 0:
        return

    try:
        result = booking_service.request_refund(current_user, booking_id)

        print("\n  Refund processed successfully!\n")
        print_field("  Original Transaction", result['original_transaction'])
        print_field("  Refund Amount", format_currency(result['refund_amount']))
        print_field("  Refund Status", result['refund_status'])
        print()

    except Exception as e:
        print(f"\n  Refund failed: {str(e)}\n")



