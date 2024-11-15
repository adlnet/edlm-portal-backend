from django.test import override_settings
from rest_framework.test import APITestCase

from users.models import User


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in EDLM Portal"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        # settings management
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

        # Auth stuff
        self.auth_email = "test_auth@test.com"
        self.auth_password = "test_auth1234"
        self.auth_first_name = "first_name_auth"
        self.auth_last_name = "last_name_auth"

        User.objects.create_user(self.auth_email,
                                 email=self.auth_email,
                                 password=self.auth_password,
                                 first_name=self.auth_first_name,
                                 last_name=self.auth_last_name,
                                 is_superuser=True)
        self.auth_user = User.objects.get(username=self.auth_email)

        self.basic_email = "test_basic@test.com"
        self.basic_password = "test_basic1234"
        self.basic_first_name = "first_name_basic"
        self.basic_last_name = "last_name_basic"

        User.objects.create_user(self.basic_email,
                                 email=self.basic_email,
                                 password=self.basic_password,
                                 first_name=self.basic_first_name,
                                 last_name=self.basic_last_name,
                                 is_superuser=True)
        self.basic_user = User.objects.get(username=self.basic_email)

        return super().setUp()
