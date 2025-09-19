import json

from django.test import tag
from django.urls import reverse
from rest_framework import status
from users.serializers import UserSerializer
from users.tests.test_setup import TestSetUp


@tag('unit')
class ValidateTests(TestSetUp):
    def test_correct_validate(self):
        """Test that the validate endpoint verifies an active session"""
        url_validate = reverse('users:validate')

        self.client.force_authenticate(user=self.user_1)

        validate_dict = {"user": UserSerializer(self.user_1).data}

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(validate_response.content.decode('utf-8')),
            validate_dict)

    def test_no_session_validate(self):
        """Test that the validate endpoint errors when no active session"""
        url_validate = reverse('users:validate')

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code,
                         status.HTTP_403_FORBIDDEN)
