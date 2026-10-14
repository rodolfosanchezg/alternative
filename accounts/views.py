"""Authentication views for setting and confirming user passwords."""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class PasswordSetView(auth_views.PasswordResetConfirmView):
    """Allow a user to set a password and then redirect to the login page."""

    success_url = reverse_lazy("login")

    def form_valid(self, form):
        """Save the password and display a success message to the user."""
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Your password has been saved. You can now sign in.",
        )

        return response
