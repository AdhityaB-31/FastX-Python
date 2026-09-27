# Tests for authentication service and operator activation.

import pytest

from services import auth_service, admin_service
from exceptions.custom_exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    AccountInactiveError,
    InvalidInputError,
    UnauthorizedActionError,
)
from decorators.decorators import require_role


class TestRegistration:
    """Test group for user and operator registration."""

    def test_register_success(self, sample_user_data):
        result = auth_service.register(**sample_user_data)
        assert result['name'] == "Test User"
        assert result['email'] == "testuser@gmail.com"
        assert result['role'] == "USER"
        assert result['is_active'] is True
        assert 'id' in result

    def test_operator_registration_inactive_by_default(self, sample_operator_data):
        result = auth_service.register(**sample_operator_data)
        assert result['role'] == "BUS_OPERATOR"
        assert result['is_active'] is False

        with pytest.raises(AccountInactiveError):
            auth_service.login(sample_operator_data['email'], sample_operator_data['password'])

    def test_operator_activation_and_deactivation(self, sample_operator_data, registered_admin):
        op_res = auth_service.register(**sample_operator_data)
        op_id = op_res['id']

        admin_service.activate_operator(registered_admin, op_id)
        login_res = auth_service.login(sample_operator_data['email'], sample_operator_data['password'])
        assert login_res['email'] == sample_operator_data['email']

        admin_service.deactivate_operator(registered_admin, op_id)
        with pytest.raises(AccountInactiveError):
            auth_service.login(sample_operator_data['email'], sample_operator_data['password'])

    def test_user_deactivation_and_reactivation(self, sample_user_data, registered_admin):
        user_res = auth_service.register(**sample_user_data)
        user_id = user_res['id']

        admin_service.deactivate_user(registered_admin, user_id)
        with pytest.raises(AccountInactiveError):
            auth_service.login(sample_user_data['email'], sample_user_data['password'])

        admin_service.activate_user(registered_admin, user_id)
        login_res = auth_service.login(sample_user_data['email'], sample_user_data['password'])
        assert login_res['email'] == sample_user_data['email']

    def test_register_duplicate_email(self, sample_user_data):
        auth_service.register(**sample_user_data)
        with pytest.raises(DuplicateEmailError):
            auth_service.register(**sample_user_data)

    def test_register_invalid_email(self, sample_user_data):
        sample_user_data['email'] = "invalid-email"
        with pytest.raises(InvalidInputError, match="Invalid email"):
            auth_service.register(**sample_user_data)

    def test_register_invalid_name(self, sample_user_data):
        sample_user_data['name'] = ""
        with pytest.raises(InvalidInputError, match="Invalid name"):
            auth_service.register(**sample_user_data)

    def test_register_invalid_phone(self, sample_user_data):
        sample_user_data['phone'] = "123"
        with pytest.raises(InvalidInputError, match="Invalid phone"):
            auth_service.register(**sample_user_data)

    def test_register_short_password(self, sample_user_data):
        sample_user_data['password'] = "abc"
        with pytest.raises(InvalidInputError, match="at least 6"):
            auth_service.register(**sample_user_data)


class TestLogin:
    """Test group for user login."""

    def test_login_success(self, sample_user_data):
        auth_service.register(**sample_user_data)
        result = auth_service.login("testuser@gmail.com", "testpass123")
        assert result['email'] == "testuser@gmail.com"
        assert result['role'] == "USER"

    def test_login_wrong_password(self, sample_user_data):
        auth_service.register(**sample_user_data)
        with pytest.raises(InvalidCredentialsError):
            auth_service.login("testuser@gmail.com", "wrongpassword")

    def test_login_nonexistent_email(self):
        with pytest.raises(InvalidCredentialsError):
            auth_service.login("nobody@gmail.com", "password")

    def test_login_empty_credentials(self):
        with pytest.raises(InvalidCredentialsError):
            auth_service.login("", "")


class TestLogout:
    """Test group for user logout."""

    def test_logout(self, registered_user):
        result = auth_service.logout(registered_user)
        assert result is None


class TestAuthorization:
    """Test group for role-based authorization decorator."""

    def test_require_role_success(self):
        @require_role("ADMIN")
        def admin_action(current_user):
            return "Admin action executed"

        admin_user = {"id": 1, "name": "Admin", "role": "ADMIN"}
        result = admin_action(admin_user)
        assert result == "Admin action executed"

    def test_require_role_failure(self):
        @require_role("ADMIN")
        def admin_action(current_user):
            return "Should not execute"

        normal_user = {"id": 1, "name": "User", "role": "USER"}
        with pytest.raises(UnauthorizedActionError):
            admin_action(normal_user)

    def test_require_role_no_user(self):
        @require_role("ADMIN")
        def admin_action(current_user):
            return "Should not execute"

        with pytest.raises(UnauthorizedActionError):
            admin_action(None)


class TestProfileManagement:
    """Test group for user and operator profile updating."""

    def test_update_user_profile_success(self, registered_user):
        user_id = registered_user['id']
        updated = auth_service.update_user_profile(
            user_id=user_id,
            name="New Name",
            phone="9876543219",
            address="New Address",
            gender="Female"
        )
        assert updated['name'] == "New Name"
        assert updated['phone'] == "9876543219"
        assert updated['address'] == "New Address"
        assert updated['gender'] == "Female"
        assert updated['email'] == registered_user['email']

    def test_update_operator_profile_success(self, sample_operator_data, registered_admin):
        op_res = auth_service.register(**sample_operator_data)
        op_id = op_res['id']
        admin_service.activate_operator(registered_admin, op_id)

        updated = auth_service.update_user_profile(
            user_id=op_id,
            name="Updated Operator",
            phone="9988776655"
        )
        assert updated['name'] == "Updated Operator"
        assert updated['phone'] == "9988776655"
        assert updated['email'] == sample_operator_data['email']

    def test_change_password_success(self, sample_user_data):
        res = auth_service.register(**sample_user_data)
        user_id = res['id']

        auth_service.update_user_profile(
            user_id=user_id,
            current_password="testpass123",
            new_password="newsecretpassword"
        )

        login_res = auth_service.login(sample_user_data['email'], "newsecretpassword")
        assert login_res['email'] == sample_user_data['email']

    def test_change_password_wrong_current_password(self, sample_user_data):
        res = auth_service.register(**sample_user_data)
        user_id = res['id']

        with pytest.raises(InvalidCredentialsError, match="incorrect"):
            auth_service.update_user_profile(
                user_id=user_id,
                current_password="wrongpassword",
                new_password="newsecretpassword"
            )

    def test_update_profile_invalid_name(self, registered_user):
        with pytest.raises(InvalidInputError, match="Invalid name"):
            auth_service.update_user_profile(user_id=registered_user['id'], name="12345")

    def test_update_profile_invalid_phone(self, registered_user):
        with pytest.raises(InvalidInputError, match="Invalid phone"):
            auth_service.update_user_profile(user_id=registered_user['id'], phone="123")

    def test_update_profile_invalid_gender(self, registered_user):
        with pytest.raises(InvalidInputError, match="Invalid gender"):
            auth_service.update_user_profile(user_id=registered_user['id'], gender="Robot")

    def test_email_cannot_be_updated(self, registered_user):
        original_email = registered_user['email']
        updated = auth_service.update_user_profile(
            user_id=registered_user['id'],
            name="New Name",
            email="hackemail@gmail.com"
        )
        assert updated['email'] == original_email


