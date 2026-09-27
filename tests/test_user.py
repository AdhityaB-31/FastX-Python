"""
Tests for User model and authentication.

Tests user model creation, encapsulation (properties),
and registration/login flows.
"""

import pytest

from models.person import Person, SystemUser
from models.user import User, PremiumUser


class TestUserModel:
    """Test group for User model operations."""

    def test_user_creation(self):
        """Test creating a User instance with default values."""
        user = User()
        assert user.name == "Unknown"
        assert user.role == "USER"

    def test_user_creation_with_args(self):
        """Test creating a User with custom arguments."""
        user = User(
            name="Adhitya",
            email="adhitya@gmail.com",
            phone="9876543210"
        )
        assert user.name == "Adhitya"
        assert user.email == "adhitya@gmail.com"
        assert user.phone == "9876543210"

    def test_user_get_dashboard(self):
        """Test User's overridden get_dashboard method."""
        user = User("Test")
        assert user.get_dashboard() == "Passenger Dashboard"

    def test_user_name_property_setter(self):
        """Test encapsulation - name property with validation."""
        user = User(name="Test")
        user.name = "New Name"
        assert user.name == "New Name"

    def test_user_name_empty_raises_error(self):
        """Test encapsulation - name setter rejects empty values."""
        user = User(name="Test")
        with pytest.raises(ValueError, match="Name cannot be empty"):
            user.name = "  "

    def test_user_str(self):
        """Test User string representation."""
        user = User(name="Test", email="test@test.com")
        result = str(user)
        assert "Test" in result

    def test_user_role(self):
        """Test User role is always USER."""
        user = User()
        assert user.get_role() == "USER"


class TestPremiumUserModel:
    """Test group for PremiumUser model."""

    def test_premium_user_creation(self):
        """Test PremiumUser creation with defaults."""
        premium = PremiumUser(name="Premium User")
        assert premium.loyalty_points == 0
        assert premium.membership_tier == "SILVER"

    def test_premium_user_dashboard(self):
        """Test PremiumUser's overridden dashboard."""
        premium = PremiumUser()
        assert premium.get_dashboard() == "Premium Passenger Dashboard"

    def test_premium_user_loyalty_points(self):
        """Test adding loyalty points."""
        premium = PremiumUser(name="Test", loyalty_points=100)
        premium.add_loyalty_points(50)
        assert premium.loyalty_points == 150

    def test_premium_user_negative_points_raises(self):
        """Test that negative loyalty points raise ValueError."""
        premium = PremiumUser()
        with pytest.raises(ValueError, match="cannot be negative"):
            premium.loyalty_points = -10

    def test_premium_user_discount(self):
        """Test discount percentage by tier."""
        silver = PremiumUser(membership_tier="SILVER")
        gold = PremiumUser(membership_tier="GOLD")
        platinum = PremiumUser(membership_tier="PLATINUM")

        assert silver.get_discount_percentage() == 5.0
        assert gold.get_discount_percentage() == 10.0
        assert platinum.get_discount_percentage() == 15.0


class TestEncapsulation:
    """Test group for encapsulation patterns."""

    def test_system_user_password_not_directly_accessible(self):
        """Test that password is name-mangled (encapsulation)."""
        user = SystemUser(name="Test", password="secret123")
        # Private attribute should not be directly accessible
        assert not hasattr(user, '__password')
        # But accessible through getter method
        assert user.get_password() == "secret123"

    def test_system_user_email_setter_validation(self):
        """Test email setter rejects empty values."""
        user = SystemUser(email="test@test.com")
        with pytest.raises(ValueError, match="Email cannot be empty"):
            user.email = ""

    def test_system_user_to_session_dict(self):
        """Test session dictionary creation."""
        user = SystemUser(name="Test", email="test@test.com",
                          role="USER", user_id=1)
        session = user.to_session_dict()
        assert session['id'] == 1
        assert session['name'] == "Test"
        assert session['email'] == "test@test.com"
        assert session['role'] == "USER"
        # Password should not be in session
        assert 'password' not in session
