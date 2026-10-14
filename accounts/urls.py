"""URL routes for authentication and password reset workflows."""

from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm, PasswordResetRequestForm
from .views import PasswordSetView

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            form_class=PasswordResetRequestForm,
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordSetView.as_view(),
        name="password_reset_confirm",
    ),
]
