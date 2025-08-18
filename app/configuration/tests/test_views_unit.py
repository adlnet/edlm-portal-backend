import json

from django.test import tag
from django.urls import reverse
from rest_framework import status

from configuration.models import Configuration

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_config_requests_pass(self):
        """Test that making a get request to the config api with a
        correct id returns the configuration"""
        conf = Configuration()
        conf.save()

        url = reverse('config:config-detail',
                      kwargs={"pk": conf.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(conf.target_xds_api,
                         responseDict['target_xds_api'])
        self.assertEqual(conf.target_elrr_api,
                         responseDict['target_elrr_api'])
        self.assertEqual(conf.target_eccr_api,
                         responseDict['target_eccr_api'])
