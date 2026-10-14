"""Management command for unlocking a user account by email."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Unlock a user account identified by its email address."""

    help = "Unlock a user account by email."

    def add_arguments(self, parser):
        """Add the required email argument to the command."""
        parser.add_argument("email")

    def handle(self, *args, **options):
        """Find the user by email and unlock the account if necessary."""
        User = get_user_model()
        email = options["email"].strip().lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f"No user found with email {email}.")

        if not user.is_locked:
            self.stdout.write(f"{email} is not locked.")
            return

        user.unlock()
        self.stdout.write(self.style.SUCCESS(f"{email} has been unlocked."))
