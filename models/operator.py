# BusOperator model class for FastX application.

from models.person import Person


class BusOperator(Person):
    """Represents a bus operator in the FastX system."""

    def __init__(self, name="Unknown", gender="Other", phone="", address="",
                 email="", password="", user_id=None, company_name="",
                 created_at="", is_active=False):
        super().__init__(name, gender, phone, address)
        self._email = email
        self.__password = password
        self._role = "BUS_OPERATOR"
        self._id = user_id
        self._company_name = company_name
        self._created_at = created_at
        self._is_active = is_active

    @property
    def email(self):
        """Get operator email."""
        return self._email

    @property
    def role(self):
        """Get operator role."""
        return self._role

    @property
    def user_id(self):
        """Get operator user ID."""
        return self._id

    @user_id.setter
    def user_id(self, value):
        """Set operator user ID."""
        self._id = value

    @property
    def company_name(self):
        """Get operator company name."""
        return self._company_name

    @company_name.setter
    def company_name(self, value):
        """Set operator company name."""
        self._company_name = value

    @property
    def created_at(self):
        """Get account creation timestamp."""
        return self._created_at

    @property
    def is_active(self):
        """Get account active status."""
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        """Set account active status."""
        self._is_active = bool(value)

    def get_password(self):
        """Get hashed password for authentication."""
        return self.__password

    def get_dashboard(self):
        """Get dashboard title for bus operator."""
        return "Operator Dashboard"

    def get_role(self):
        """Get role of bus operator."""
        return "BUS_OPERATOR"

    def to_session_dict(self):
        """Convert operator data to session dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "role": self._role,
            "is_active": self._is_active
        }

    def __str__(self):
        """Return string representation."""
        return f"Operator: {self._name} ({self._email})"

    def __repr__(self):
        """Return detailed representation."""
        return (f"BusOperator(name='{self._name}', email='{self._email}', "
                f"user_id={self._id})")

