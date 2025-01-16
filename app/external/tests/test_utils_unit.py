import json
from unittest.mock import Mock, patch

from django.test import tag

from configuration.models import Configuration
from external.models import Course
from external.utils.eccr_utils import (get_eccr_data_api_url,
                                       get_eccr_search_api_url)
from external.utils.xds_utils import (TokenAuth, format_metadata,
                                      get_course_name, get_courses_api_url,
                                      get_xds_experience,
                                      handle_unauthenticated_user,
                                      metadata_to_target, save_courses)

from .test_setup import TestSetUp


@tag('unit')
class UtilsTests(TestSetUp):

    def test_xds_get_course_name(self):
        """Test that util extracts course name"""
        expected = "abc"
        course = {"Course": {"CourseTitle": expected}}
        resp = Mock()
        resp.json.return_value = json.dumps(course)

        ret = get_course_name(resp)

        self.assertEqual(ret, expected)

    def test_xds_no_get_course_name(self):
        """Test that util returns None if no course title"""
        course = {"key": "value"}
        expected = None
        resp = Mock()
        resp.json.return_value = json.dumps(course)

        ret = get_course_name(resp)

        self.assertEqual(ret, expected)

    def test_xds_format_metadata(self):
        """Test that util reformats metadata"""
        expected = {"key": "my ledger",
                    "Supplemental_Ledger": None,
                    "meta": {"id": "abc123",
                             "metadata_key_hash": "shashasha"}}
        course = {"metadata": {"Metadata_Ledger": {"key": "my ledger"}},
                  "unique_record_identifier": "abc123",
                  "metadata_key_hash": "shashasha"}

        ret = format_metadata(course)

        self.assertDictEqual(ret, expected)

    def test_xds_metadata_to_target(self):
        """Test that util reformats metadata"""
        expected = {"key": "my ledger",
                    "Supplemental_Ledger": None,
                    "meta": {"id": "abc123",
                             "metadata_key_hash": "shashasha"}}
        course = {"metadata": {"Metadata_Ledger": {"key": "my ledger"}},
                  "unique_record_identifier": "abc123",
                  "metadata_key_hash": "shashasha"}

        ret = metadata_to_target(json.dumps(course))

        self.assertDictEqual(ret, expected)

    def test_xds_metadata_to_target_list(self):
        """Test that util reformats metadata lists"""
        expected = [{"key": "my ledger",
                    "Supplemental_Ledger": None,
                     "meta": {"id": "abc123",
                              "metadata_key_hash": "shashasha"}}]
        course = [{"metadata": {"Metadata_Ledger": {"key": "my ledger"}},
                  "unique_record_identifier": "abc123",
                   "metadata_key_hash": "shashasha"}]

        ret = metadata_to_target(json.dumps(course))

        self.assertDictEqual(ret[0], expected[0])

    def test_xds_get_courses_api_url(self):
        """Test that util gets api url"""
        xds_api = "https://example.com"
        course_id = "abc123"
        expected = xds_api + "/api/experiences/" + course_id
        conf = Configuration(target_xds_api=xds_api)
        conf.save()

        ret = get_courses_api_url(course_id)

        self.assertEqual(ret, expected)

    def test_xds_save_courses(self):
        """Test that util saves course lists"""
        courses = [
            ("shashasha", "title0"),
            ("shashasha2", "title2"),
            ("shashasha", "title3")
        ]

        save_courses(courses)

        self.assertEqual(Course.objects.all().count(), 2)

    def test_eccr_get_eccr_search_api_url(self):
        """Test that util gets eccr search api url"""
        eccr_api = "https://example.com"
        expected = eccr_api + "/api/sky/repo/search/"
        conf = Configuration(target_eccr_api=eccr_api)
        conf.save()

        ret = get_eccr_search_api_url()

        self.assertEqual(ret, expected)

    def test_eccr_get_eccr_data_api_url(self):
        """Test that util gets eccr search api url"""
        eccr_api = "https://example.com"
        expected = eccr_api + "/api/data/"
        conf = Configuration(target_eccr_api=eccr_api)
        conf.save()

        ret = get_eccr_data_api_url()

        self.assertEqual(ret, expected)

    def test_handle_unauthenticated_user(self):
        """Test that 401 response is returned"""
        expected = 401
        actual = handle_unauthenticated_user()

        self.assertEqual(actual.status_code, expected)

    def test_token_auth(self):
        """Test that Token Auth is created correctly"""
        token = "abc"
        expected = "abc"
        actual = TokenAuth(token)
        req = Mock()
        req.headers = {}
        actual(req)

        self.assertEqual(actual.token, expected)
        self.assertIn('Authorization', req.headers)
        self.assertIn(token, req.headers['Authorization'])
        self.assertIn('Bearer', req.headers['Authorization'])

    def test_get_xds_exp(self):
        """Test that xds request is correctly formatted"""
        exp_id = "xyz"
        expected = None
        xds_api = "https://example.com"
        conf = Configuration(target_xds_api=xds_api)
        conf.save()
        with patch('external.utils.xds_utils.requests') as req:
            req.get.return_value = None
            actual = get_xds_experience(exp_id)

            self.assertEqual(actual, expected)
            req.get.assert_called_once()
            self.assertIn(exp_id, req.get.call_args[0][0])

    def test_get_xds_exp_with_auth(self):
        """Test that xds request is correctly formatted"""
        token = "abc"
        auth = TokenAuth(token)
        exp_id = "xyz"
        expected = None
        xds_api = "https://example.com"
        conf = Configuration(target_xds_api=xds_api)
        conf.save()
        with patch('external.utils.xds_utils.requests') as req:
            req.get.return_value = None
            actual = get_xds_experience(exp_id, auth=auth)

            self.assertEqual(actual, expected)
            req.get.assert_called_once()
            self.assertIn(exp_id, req.get.call_args[0][0])
            self.assertEqual(auth, req.get.call_args[1]['auth'])
