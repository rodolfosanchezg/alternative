"""Forms for authentication, password reset, and user administration."""

from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model

User = get_user_model()

INVALID_LOGIN_MESSAGE = "Invalid email or password."


class LoginForm(auth_forms.AuthenticationForm):
    """Authentication form configured for email-based login."""

    error_messages = {
        "invalid_login": INVALID_LOGIN_MESSAGE,
        "inactive": INVALID_LOGIN_MESSAGE,
    }

    def __init__(self, *args, **kwargs):
        """Initialize the login form and configure the email field."""
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget = forms.EmailInput(
            attrs={"autofocus": True, "autocomplete": "email"}
        )


class PasswordResetRequestForm(auth_forms.PasswordResetForm):
    """Password reset form that includes eligible passwordless accounts."""

    def get_users(self, email):
        """Return active and unlocked users matching the supplied email."""
        # Unlike Django's default, include accounts that don't have a password yet.
        return User._default_manager.filter(
            email=email.strip().lower(),
            is_active=True,
            is_locked=False,
        )


class AdminUserCreationForm(forms.ModelForm):
    """Form used by administrators to create application users."""

    class Meta:
        """Configure the user model and fields exposed by the form."""

        model = User
        fields = ["email", "first_name", "last_name", "job_title", "role"]

    def clean_email(self):
        """Normalize the submitted email address."""
        return self.cleaned_data["email"].strip().lower()

    def save(self, commit=True):
        """Save a new user with an unusable password by default."""
        user = super().save(commit=False)
        user.set_unusable_password()

        if commit:
            user.save()

        return user


class AdminUserChangeForm(auth_forms.UserChangeForm):
    """Form used by administrators to update existing users."""

    class Meta:
        """Configure the user model and expose all editable fields."""

        model = User
        fields = "__all__"

    def clean_email(self):
        """Normalize the submitted email address."""
        return self.cleaned_data["email"].strip().lower()
