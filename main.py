"""
FastX - Online Bus Ticket Booking System
Python Console-Level Application

Entry point for the FastX application.
Initializes the database, seeds data, configures logging,
and launches the main menu.

Usage:
    python main.py
"""

import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging():
    """Configure the Python logging system.

    Sets up logging to both console and file with appropriate
    formatting and log levels.
    """
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "fastx.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Suppress verbose MySQL logging
    logging.getLogger('mysql.connector').setLevel(logging.WARNING)


def initialize_application():
    """Initialize the FastX application.

    Creates database tables and seeds initial data.
    """
    from database.schema import create_tables
    from database.seed import seed_database

    print()
    print("=" * 50)
    print(f"{'FASTX':^50}")
    print(f"{'Online Bus Ticket Booking System':^50}")
    print("=" * 50)
    print()
    print("  Initializing application...")

    # Create database tables
    create_tables()
    print("  ✓ Database tables ready.")

    # Seed initial data
    seed_database()
    print("  ✓ Application initialized.\n")


def main():
    """Main entry point for the FastX application."""
    # Setup logging first
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("FastX application starting...")

    try:
        # Initialize database and seed data
        initialize_application()

        # Launch main menu
        from cli.main_menu import main_menu
        main_menu()

    except KeyboardInterrupt:
        print("\n\n  Application interrupted. Goodbye!\n")
        logger.info("Application interrupted by user.")
    except Exception as e:
        logger.error("Application error: %s", str(e))
        print(f"\n  A critical error occurred: {str(e)}")
        print("  Please check the log file at data/fastx.log\n")
    finally:
        logger.info("FastX application stopped.")


if __name__ == "__main__":
    main()
