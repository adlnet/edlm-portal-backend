from django.test import tag
from rest_framework.test import APITestCase

from users.models import Organization


@tag('unit')
class ModelTests(APITestCase):

    def test_org(self):
        """Test that creating an Organization is successful"""
        name = 'org a'
        org = Organization(name=name)
        org.save()

        self.assertEqual(org.name, name)
        self.assertEqual(str(org), name)

    def test_org_with_parent(self):
        """Test that creating an Organization is successful"""
        name = 'org a'
        name_2 = 'org b'
        org = Organization(name=name)
        org.save()
        org_2 = Organization(name=name_2, parent=org)
        org_2.save()

        self.assertEqual(org.name, name)
        self.assertEqual(str(org), name)
        self.assertEqual(org_2.name, name_2)
        self.assertEqual(org_2.parent, org)
        self.assertIn(name_2, str(org_2))
        self.assertIn(str(org), str(org_2))
