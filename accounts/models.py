"""Custom user model, roles, and authentication-related account behavior."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    """Available application roles for users."""

    ADMIN = "admin", "Admin"
    RECRUITER = "recruiter", "Recruiter"
    VIEWER = "viewer", "Viewer"


class UserManager(BaseUserManager):
    """Manager for creating and retrieving users identified by email."""

    user_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and persist a user with a normalized email address."""
        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            # Accounts created without a password get one through an email link.
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fiels):
        """Create and persist a regular application user."""
        extra_fiels.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fiels)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and persist an administrator with superuser privileges."""
        extra_fields["is_superuser"] = True
        extra_fields["role"] = Role.ADMIN
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        """Return a user matching the supplied email address."""
        return self.get(email=email.strip().lower())


class User(AbstractUser):
    """Custom application user authenticated by email instead of username."""

    MAX_FAILED_LOGIN_ATTEMPTS = 4

    username = None
    email = models.EmailField("email address", unique=True)
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    job_title = models.CharField("job title", max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)

    is_locked = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        """Return the user's email address as its string representation."""
        return self.email

    def save(self, *args, **kwargs):
        """Normalize user data and enforce admin access rules before saving."""
        if self.email:
            self.email = self.email.strip().lower()

        if self.is_superuser:
            self.role = Role.ADMIN

        # Only superusers can access the Django admin.
        self.is_staff = self.is_superuser

        super().save(*args, **kwargs)

    # Account status

    @property
    def status(self):
        """Return the current account status."""
        if not self.is_active:
            return "deactivated"
        if self.is_locked:
            return "locked"
        return "active"

    # Roles

    @property
    def is_admin_role(self):
        """Return whether the user has the application administrator role."""
        return self.role == Role.ADMIN

    @property
    def can_edit_records(self):
        """Return whether the user's role permits editing application records."""
        return self.role in (Role.ADMIN, Role.RECRUITER)

    # Failed login attempts

    def register_failed_login(self):
        """Record a failed login and return whether it locked the account."""
        self.failed_login_attempts += 1
        just_locked = (
            not self.is_locked
            and self.failed_login_attempts >= self.MAX_FAILED_LOGIN_ATTEMPTS
        )
        if just_locked:
            self.is_locked = True
            self.locked_at = timezone.now()
        self.save(update_fields=["failed_login_attempts", "is_locked", "locked_at"])
        return just_locked

    def reset_failed_logins(self):
        """Reset the number of failed login attempts after successful login."""
        if self.failed_login_attempts:
            self.failed_login_attempts = 0
            self.save(update_fields=["failed_login_attempts"])

    def unlock(self):
        """Unlock the account and clear all failed-login tracking data."""
        self.is_locked = False
        self.failed_login_attempts = 0
        self.locked_at = None
        self.save(update_fields=["is_locked", "failed_login_attempts", "locked_at"])
