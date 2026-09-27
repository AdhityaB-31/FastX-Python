# User and PremiumUser model classes for FastX application.

from models.person import SystemUser


class User(SystemUser):
    """Represents a passenger user in the FastX system."""

    def __init__(self, name="Unknown", gender="Other", phone="", address="",
                 email="", password="", user_id=None, created_at=""):
        super().__init__(
            name=name, gender=gender, phone=phone, address=address,
            email=email, password=password, role="USER",
            user_id=user_id, created_at=created_at
        )

    def get_dashboard(self):
        """Get dashboard title for passenger."""
        return "Passenger Dashboard"

    def __str__(self):
        """Return string representation."""
        return f"Passenger: {self._name} ({self._email})"

    def __repr__(self):
        """Return detailed representation."""
        return (f"User(name='{self._name}', email='{self._email}', "
                f"user_id={self._id})")


class PremiumUser(User):
    """Represents a premium passenger with loyalty benefits."""

    def __init__(self, name="Unknown", gender="Other", phone="", address="",
                 email="", password="", user_id=None, created_at="",
                 loyalty_points=0, membership_tier="SILVER"):
        super().__init__(
            name=name, gender=gender, phone=phone, address=address,
            email=email, password=password, user_id=user_id,
            created_at=created_at
        )
        self._loyalty_points = loyalty_points
        self._membership_tier = membership_tier

    @property
    def loyalty_points(self):
        """Get user's loyalty points."""
        return self._loyalty_points

    @loyalty_points.setter
    def loyalty_points(self, value):
        """Set user's loyalty points."""
        if value < 0:
            raise ValueError("Loyalty points cannot be negative.")
        self._loyalty_points = value

    @property
    def membership_tier(self):
        """Get user's membership tier."""
        return self._membership_tier

    def get_dashboard(self):
        """Get dashboard title for premium passenger."""
        return "Premium Passenger Dashboard"

    def add_loyalty_points(self, points):
        """Add loyalty points for booking."""
        self._loyalty_points += points

    def get_discount_percentage(self):
        """Get discount percentage based on tier."""
        discounts = {
            "SILVER": 5.0,
            "GOLD": 10.0,
            "PLATINUM": 15.0
        }
        return discounts.get(self._membership_tier, 0.0)

    def __str__(self):
        """Return string representation."""
        return (f"Premium Passenger: {self._name} "
                f"({self._membership_tier}, {self._loyalty_points} pts)")

    def __repr__(self):
        """Return detailed representation."""
        return (f"PremiumUser(name='{self._name}', email='{self._email}', "
                f"tier='{self._membership_tier}', points={self._loyalty_points})")

