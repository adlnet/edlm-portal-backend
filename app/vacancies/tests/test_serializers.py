from django.test import tag
from rest_framework.test import APITestCase

from external.models import Job
from vacancies.models import Vacancy
from vacancies.serializers import VacancySerializer


@tag('unit')
class SerializerTests(APITestCase):

    def test_vacancy_serializer(self):
        """Test that creating an Vacancy is successful"""
        key = 'abc'
        key_hash = 'xyz'
        base = 'value'
        url = "https://www.google.com"
        vac_ser = VacancySerializer(
            data={"vacancy_key": key, "vacancy_key_hash": key_hash,
                  "JobTitle": base, "JobPostingID": base,
                  "JobPostingSite": url, "OrganizationName": base,
                  "ProviderName": base, "UIDUnitIdentifiers": base})
        vac_ser.is_valid(raise_exception=True)
        vac_ser.save()

        vac = vac_ser.instance

        self.assertEqual(vac.vacancy_key, key)
        self.assertEqual(vac.vacancy_key_hash, key_hash)
        self.assertEqual(str(vac), key)
        self.assertIsInstance(vac, Vacancy)

    def test_vacancy_serializer_with_job(self):
        """Test that creating an Vacancy is successful"""
        name = "job_name"
        reference = "job_ref"
        job_type = "job_type"

        job = Job(name=name, job_type=job_type,
                  reference=reference)
        job.save()
        key = 'abc'
        key_hash = 'xyz'
        base = 'value'
        url = "https://www.google.com"
        vac_ser = VacancySerializer(
            data={"vacancy_key": key, "vacancy_key_hash": key_hash,
                  "JobTitle": base, "JobPostingID": base,
                  "JobPostingSite": url, "OrganizationName": base,
                  "ProviderName": base, "UIDUnitIdentifiers": base, 'job': {
                      'reference': job.reference
                  }
                  })
        vac_ser.is_valid(raise_exception=True)
        vac_ser.save()

        vac = vac_ser.instance

        self.assertEqual(vac.vacancy_key, key)
        self.assertEqual(vac.vacancy_key_hash, key_hash)
        self.assertEqual(vac.job, job)
        self.assertEqual(str(vac), key)
        self.assertIsInstance(vac, Vacancy)
