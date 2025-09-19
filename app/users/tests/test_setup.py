from rest_framework.test import APITestCase
from users.models import User
from django.test import override_settings


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in User"""
    def setUp(self):
        """Function to set up necessary data for testing"""

        self.settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        self.settings_manager.enable()
        self.addCleanup(self.settings_manager.disable)

        self.user_1_email = "test3@test.com"
        self.user_1_password = "1234"

        self.user_1 = User.objects.create_user(
            self.user_1_email,
            self.user_1_password,
            first_name="john",
            last_name="doe"
        )

        return super().setUp()

    def tearDown(self):
        """Function to clean up"""
        return super().tearDown()
