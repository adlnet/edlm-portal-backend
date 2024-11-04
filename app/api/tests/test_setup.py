from rest_framework.test import APITestCase

from api.models import ProfileAnswer, ProfileQuestion
from users.models import User


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in EDLM Portal"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        # Auth stuff
        self.auth_email = "test_auth@test.com"
        self.auth_password = "test_auth1234"
        self.auth_first_name = "first_name_auth"
        self.auth_last_name = "last_name_auth"

        User.objects.create_user(self.auth_email,
                                 password=self.auth_password,
                                 first_name=self.auth_first_name,
                                 last_name=self.auth_last_name,
                                 is_superuser=True)
        self.auth_user = User.objects.get(username=self.auth_email)

        # Profile Question
        active = True
        order = 32
        question = "What color is the sky?"

        self.pq = ProfileQuestion(active=active,
                                  order=order,
                                  question=question)

        # Profile Answer
        order = 32
        answer = "Blue"

        self.pa = ProfileAnswer(question=self.pq,
                                order=order,
                                answer=answer)
        order_2 = 13
        answer_2 = "Green"

        self.pa_2 = ProfileAnswer(question=self.pq,
                                  order=order_2,
                                  answer=answer_2)

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
