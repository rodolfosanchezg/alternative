"""Custom Django authentication backend using email-based login."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .emails import send_account_locked_email

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate users by email and enforce account lockout rules."""

    def user_can_authenticate(self, user):
        """Return whether the user is active and not locked."""
        # Deactivated (is_active=False) and locked accounts cannot sign in,
        # and their open sessions stop being valid on the next request.
        return super().user_can_authenticate(user) and not getattr(
            user, "is_locked", False
        )

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate a user and track failed login attempts."""
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Hash the password anyway so response times don't reveal
            # whether the email exists.
            UserModel().set_password(password)
            return None

        if not self.user_can_authenticate(user):
            return None

        if user.check_password(password):
            user.reset_failed_logins()
            return user

        if user.register_failed_login():
            send_account_locked_email(user)
        return None
