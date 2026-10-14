"""Email helpers for account-related notifications."""

from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_account_locked_email(user):
    """Send an account-lock notification email to the specified user."""
    body = render_to_string("emails/account_locked.txt", {"user": user})
    send_mail(
        subject="Your Alternative account has been locked",
        message=body,
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
    )
