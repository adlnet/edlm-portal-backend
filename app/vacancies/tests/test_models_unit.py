from django.test import tag
from rest_framework.test import APITestCase

from vacancies.models import Vacancy


@tag('unit')
class ModelTests(APITestCase):

    def test_vacancy(self):
        """Test that creating an Vacancy is successful"""
        key = 'abc'
        key_hash = 'xyz'
        vac = Vacancy(vacancy_key=key, vacancy_key_hash=key_hash)
        vac.save()

        self.assertEqual(vac.vacancy_key, key)
        self.assertEqual(vac.vacancy_key_hash, key_hash)
        self.assertEqual(str(vac), key)
