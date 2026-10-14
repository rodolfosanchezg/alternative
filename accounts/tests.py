from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PASSWORD = "Str0ng-Passw0rd!"
INVALID = "Invalid email or password."


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ana@example.com",
            password=PASSWORD,
            first_name="Ana",
            last_name="Gomez",
            role="recruiter",
        )

    def login(self, email, password):
        return self.client.post(
            reverse("login"), {"username": email, "password": password}
        )

    def fail_login(self, times):
        for _ in range(times):
            self.login("ana@example.com", "wrong-password")

    def test_l02_email_is_stored_lowercase(self):
        user = User.objects.create_user(
            email="Laura@Example.COM", first_name="Laura", last_name="Ruiz"
        )
        self.assertEqual(user.email, "laura@example.com")

    def test_l02_login_is_case_insensitive(self):
        response = self.login("ANA@Example.com", PASSWORD)
        self.assertRedirects(response, reverse("board"))

    def test_l04_default_role_is_viewer(self):
        user = User.objects.create_user(
            email="pedro@example.com", first_name="Pedro", last_name="Diaz"
        )
        self.assertEqual(user.role, "viewer")

    def test_l05_superuser_gets_admin_role_and_django_admin_access(self):
        admin = User.objects.create_superuser(
            email="Root@Example.com",
            password=PASSWORD,
            first_name="Root",
            last_name="User",
        )
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)

    def test_l08_regular_users_have_no_django_admin_access(self):
        self.assertFalse(self.user.is_staff)

    def test_l19_same_message_for_wrong_password_and_unknown_email(self):
        self.assertContains(self.login("ana@example.com", "wrong-password"), INVALID)
        self.assertContains(self.login("nobody@example.com", "wrong-password"), INVALID)

    def test_l22_locked_user_session_ends(self):
        self.client.force_login(self.user)
        self.user.is_locked = True
        self.user.save()
        response = self.client.get(reverse("board"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('board')}")

    def test_l23_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))

    def test_l24_account_locks_on_fourth_failed_attempt(self):
        self.fail_login(3)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked)
        self.fail_login(1)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked)

    def test_l24_successful_login_resets_counter(self):
        self.fail_login(3)
        self.login("ana@example.com", PASSWORD)
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_l25_locked_account_gets_email_and_cannot_sign_in(self):
        self.fail_login(4)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("locked", mail.outbox[0].subject)
        self.assertContains(self.login("ana@example.com", PASSWORD), INVALID)

    def test_l27_unlock_resets_state(self):
        self.fail_login(4)
        self.user.refresh_from_db()
        self.user.unlock()
        self.assertRedirects(self.login("ana@example.com", PASSWORD), reverse("board"))

    def test_l28_reset_link_sent_to_account_without_password(self):
        User.objects.create_user(
            email="pedro@example.com", first_name="Pedro", last_name="Diaz"
        )
        self.client.post(reverse("password_reset"), {"email": "Pedro@Example.com"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["pedro@example.com"])

    def test_l28_reset_link_not_sent_to_locked_account(self):
        self.user.is_locked = True
        self.user.save()
        response = self.client.post(
            reverse("password_reset"), {"email": "ana@example.com"}
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_l28_reset_link_not_sent_to_deactivated_account(self):
        self.user.is_active = False
        self.user.save()
        self.client.post(reverse("password_reset"), {"email": "ana@example.com"})
        self.assertEqual(len(mail.outbox), 0)
