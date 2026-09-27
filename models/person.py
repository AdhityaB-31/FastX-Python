# Person and SystemUser model classes for FastX application.


class Person:
    """Base class representing a person in the FastX system."""

    def __init__(self, name="Unknown", gender="Other", phone="", address=""):
        self._name = name
        self._gender = gender
        self._phone = phone
        self._address = address

    @property
    def name(self):
        """Get the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the person's name with validation."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def gender(self):
        """Get the person's gender."""
        return self._gender

    @gender.setter
    def gender(self, value):
        """Set the person's gender."""
        self._gender = value

    @property
    def phone(self):
        """Get the person's phone number."""
        return self._phone

    @phone.setter
    def phone(self, value):
        """Set the person's phone number."""
        self._phone = value

    @property
    def address(self):
        """Get the person's address."""
        return self._address

    @address.setter
    def address(self, value):
        """Set the person's address."""
        self._address = value

    def get_dashboard(self):
        """Get dashboard title for person."""
        return "General Dashboard"

    def get_role(self):
        """Get role of person."""
        return "PERSON"

    def __str__(self):
        """Return string representation."""
        return f"{self._name} ({self.get_role()})"

    def __repr__(self):
        """Return detailed representation."""
        return (f"Person(name='{self._name}', gender='{self._gender}', "
                f"phone='{self._phone}', address='{self._address}')")


class SystemUser(Person):
    """Represents a system user with authentication credentials."""

    def __init__(self, name="Unknown", gender="Other", phone="", address="",
                 email="", password="", role="USER", user_id=None, created_at=""):
        super().__init__(name, gender, phone, address)
        self._email = email
        self.__password = password
        self._role = role
        self._id = user_id
        self._created_at = created_at

    @property
    def email(self):
        """Get the user's email."""
        return self._email

    @email.setter
    def email(self, value):
        """Set user's email with validation."""
        if not value or not value.strip():
            raise ValueError("Email cannot be empty.")
        self._email = value.strip()

    @property
    def role(self):
        """Get the user's role."""
        return self._role

    @property
    def user_id(self):
        """Get the user's ID."""
        return self._id

    @user_id.setter
    def user_id(self, value):
        """Set the user's ID."""
        self._id = value

    @property
    def created_at(self):
        """Get account creation timestamp."""
        return self._created_at

    def get_password(self):
        """Get hashed password for authentication."""
        return self.__password

    def set_password(self, new_password):
        """Set new hashed password."""
        self.__password = new_password

    def get_role(self):
        """Get role of system user."""
        return self._role

    def get_dashboard(self):
        """Get dashboard title for system user."""
        return "System User Dashboard"

    def to_session_dict(self):
        """Convert user data to session dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "role": self._role
        }

    def __str__(self):
        """Return string representation."""
        return f"{self._name} ({self._role}) - {self._email}"

    def __repr__(self):
        """Return detailed representation."""
        return (f"SystemUser(name='{self._name}', email='{self._email}', "
                f"role='{self._role}', user_id={self._id})")

