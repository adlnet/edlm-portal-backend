from django.core.exceptions import ValidationError
from django.test import tag

from configuration.models import Configuration

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_configuration(self):
        """Test that creating a Configuration is successful"""
        xds = "xds"
        xms = "xms"

        conf = Configuration(target_xds_api=xds,
                             target_xms_api=xms)
        conf.full_clean()
        conf.save()

        self.assertEqual(conf.target_xds_api, xds)
        self.assertEqual(conf.target_xms_api, xms)
        self.assertEqual(Configuration.objects.all().count(), 1)

    def test_multiple_configuration(self):
        """Test that creating 2 Configurations fails"""
        xds = "xds"
        xms = "xms"
        error_msg = "['There can only be one Configuration instance']"

        conf = Configuration(target_xds_api=xds,
                             target_xms_api=xms)
        conf.full_clean()
        conf.save()

        conf2 = Configuration(target_xds_api=xds,
                              target_xms_api=xms)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 conf2.save)
        self.assertEqual(conf.target_xds_api, xds)
        self.assertEqual(conf.target_xms_api, xms)
        self.assertEqual(Configuration.objects.all().count(), 1)
