# Admin model class for FastX application.

from models.person import SystemUser


class Admin(SystemUser):
    """Represents an administrator in the FastX system."""

    def __init__(self, name="Unknown", gender="Other", phone="", address="",
                 email="", password="", user_id=None, created_at="",
                 admin_level="STANDARD"):
        super().__init__(
            name=name, gender=gender, phone=phone, address=address,
            email=email, password=password, role="ADMIN",
            user_id=user_id, created_at=created_at
        )
        self._admin_level = admin_level

    @property
    def admin_level(self):
        """Get admin privilege level."""
        return self._admin_level

    @admin_level.setter
    def admin_level(self, value):
        """Set admin privilege level."""
        valid_levels = ['STANDARD', 'SUPER']
        if value not in valid_levels:
            raise ValueError(f"Invalid admin level. Must be one of: {valid_levels}")
        self._admin_level = value

    def get_dashboard(self):
        """Get dashboard title for administrator."""
        return "Admin Dashboard"

    def __str__(self):
        """Return string representation."""
        return f"Admin: {self._name} ({self._admin_level})"

    def __repr__(self):
        """Return detailed representation."""
        return (f"Admin(name='{self._name}', email='{self._email}', "
                f"admin_level='{self._admin_level}', user_id={self._id})")

