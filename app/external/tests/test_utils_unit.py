import json
from unittest.mock import Mock, patch

from dateutil.relativedelta import relativedelta
from django.test import tag
from django.utils import timezone

from configuration.models import Configuration
from external.models import Course
from external.utils.eccr_utils import (get_eccr_data_api_url, get_eccr_item,
                                       get_eccr_search_api_url,
                                       validate_eccr_item)
from external.utils.elrr_utils import (TokenAuth as ElrrTokenAuth,
                                       calculate_goal_achieved_by_date,
                                       create_elrr_goal,
                                       create_elrr_person,
                                       get_elrr_api_url,
                                       get_elrr_goal,
                                       get_elrr_person_id_by_email,
                                       get_or_create_elrr_competency,
                                       get_or_create_elrr_learning_resource,
                                       get_or_create_elrr_person_by_email,
                                       remove_course_from_elrr_goal,
                                       remove_goal_from_elrr,
                                       remove_ksa_from_elrr_goal,
                                       update_elrr_goal,
                                       validate_elrr_competency,
                                       validate_elrr_goal,
                                       validate_elrr_learning_resource,
                                       validate_person)
from external.utils.xds_utils import (TokenAuth, format_metadata,
                                      get_course_name, get_courses_api_url,
                                      get_xds_experience,
                                      handle_unauthenticated_user,
                                      metadata_to_target, save_courses,
                                      validate_xds_course)

from .test_setup import TestSetUp


@tag('unit')
class UtilsTests(TestSetUp):

    def test_xds_get_course_name(self):
        """Test that util extracts course name"""
        expected = "abc"
        course = {"p2881-core": {"Title": expected}}
        resp = Mock()
        resp.json.return_value = course

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

    def test_get_eccr_item(self):
        """Test that eccr request is correctly formatted"""
        item_type = "test_type"
        item_id = "12345"
        expected = None
        eccr_api = "https://example.com"
        conf = Configuration(target_eccr_api=eccr_api)
        conf.save()
        with patch('external.utils.eccr_utils.requests') as req:
            req.get.return_value = None
            actual = get_eccr_item(item_id, item_type)

            self.assertEqual(actual, expected)
            req.get.assert_called_once()
            expected_url = f"{eccr_api}/api/data/{item_type}/{item_id}"
            self.assertEqual(expected_url, req.get.call_args[0][0])

    def test_get_eccr_item_with_auth(self):
        """Test that eccr request is correctly formatted"""
        token = "abc"
        auth = TokenAuth(token)
        item_type = "test_type"
        item_id = "12345"
        expected = None
        eccr_api = "https://example.com"
        conf = Configuration(target_eccr_api=eccr_api)
        conf.save()
        with patch('external.utils.eccr_utils.requests') as req:
            req.get.return_value = None
            actual = get_eccr_item(item_id, item_type, auth=auth)

            self.assertEqual(actual, expected)
            req.get.assert_called_once()
            expected_url = f"{eccr_api}/api/data/{item_type}/{item_id}"
            self.assertEqual(expected_url, req.get.call_args[0][0])

    def test_validate_eccr_item(self):
        """Test that util validates eccr item"""
        reference = "test_framework/12345"
        expected_name = "Test Framework 7"
        eccr_api = "https://example.com"
        conf = Configuration(target_eccr_api=eccr_api)
        conf.save()

        with patch('external.utils.eccr_utils.get_eccr_item') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {
                'name': {'@value': expected_name}
            }

            req.return_value = resp

            actual = validate_eccr_item(reference)

            self.assertEqual(actual, expected_name)
            req.assert_called_once_with(id="12345", item_type="test_framework")

    def test_validate_xds_course(self):
        """Test that util validates xds course"""
        reference = "bbc123"
        expected_name = "Test Course ABC"
        xds_api = "https://example.com"
        conf = Configuration(target_xds_api=xds_api)
        conf.save()

        with patch('external.utils.xds_utils.get_xds_experience') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {
                "p2881-core": {"Title": expected_name}
            }

            req.return_value = resp

            actual = validate_xds_course(reference)

            self.assertEqual(actual, expected_name)
            req.assert_called_once_with(experience_id=reference)

    def test_elrr_get_elrr_api_url(self):
        """Test that elrr util gets api url"""
        elrr_api = "https://elrr-example.com"
        expected = elrr_api + "/api/"
        conf = Configuration(target_elrr_api=elrr_api)
        conf.save()

        ret = get_elrr_api_url()

        self.assertEqual(ret, expected)

    def test_elrr_token_auth(self):
        """Test the ELRR Token Auth"""
        token = "test_elrr_token_998"
        expected = "test_elrr_token_998"
        actual = ElrrTokenAuth(token)
        req = Mock()
        req.headers = {}
        actual(req)

        self.assertEqual(actual.token, expected)
        self.assertIn('Authorization', req.headers)
        self.assertIn(token, req.headers['Authorization'])
        self.assertIn('Bearer', req.headers['Authorization'])

    def test_elrr_validate_person(self):
        """Test person validation with full name"""
        person = {
            'firstName': 'Test',
            'lastName': 'DDD',
        }

        self.assertTrue(validate_person(person))

    def test_elrr_validate_person_missing_name(self):
        """Test person validation fails without first/last name"""
        person = {
            'firstName': 'Test',
        }

        self.assertFalse(validate_person(person))

        person = {
            'lastName': 'DDD',
        }

        self.assertFalse(validate_person(person))

    def test_elrr_validate_elrr_goal_missing_id(self):
        """Test goal validation fails without id"""
        goal_data = {
            'name': 'Test Goal',
        }

        with self.assertRaises(ValueError):
            validate_elrr_goal(goal_data)

    def test_elrr_validate_elrr_competency_missing_id(self):
        """Test competency validation fails without id"""
        competency_data = {
            'statement': 'Test Competency',
        }

        with self.assertRaises(ValueError):
            validate_elrr_competency(competency_data)

    def test_elrr_validate_elrr_learning_resource_missing_id(self):
        """Test learning resource validation fails without id"""
        learning_resource_data = {
            'title': 'Test Learning Resource',
        }

        with self.assertRaises(ValueError):
            validate_elrr_learning_resource(learning_resource_data)

    def test_elrr_get_elrr_person_id_by_email(self):
        """Test getting person ID by email"""
        email = 'test@test.com'
        person_id = '232-443-665-778'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()
        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = [{
                'id': person_id,
                'firstName': 'Tester',
                'lastName': 'Johny',
            }]

            req.get.return_value = resp

            actual = get_elrr_person_id_by_email(email)

            self.assertEqual(actual, person_id)
            req.get.assert_called_once()

    def test_elrr_get_elrr_person_id_by_email_not_found(self):
        """Test getting person ID by email when not found"""
        email = 'noone@example.com'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = []

            req.get.return_value = resp

            actual = get_elrr_person_id_by_email(email)

            self.assertIsNone(actual)

    def test_elrr_crete_elrr_person(self):
        """Test creating a person in ELRR"""
        person_id = '555-666-777-888'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 201
            resp.json.return_value = {
                'id': person_id,
                'firstName': self.auth_user.first_name,
                'lastName': self.auth_user.last_name,
            }
            req.post.return_value = resp

            actual = create_elrr_person(self.auth_user)

            self.assertEqual(actual, person_id)
            req.post.assert_called_once()

    def test_elrr_get_or_create_elrr_person_by_email_existing(self):
        """Test get or create a person in ELRR by email when existing"""
        person_id = '012-834-678-666'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with (patch('external.utils.elrr_utils.get_elrr_person_id_by_email')
              as get_mock):
            get_mock.return_value = person_id

            actual = get_or_create_elrr_person_by_email(self.auth_user)

            self.assertEqual(actual, person_id)
            get_mock.assert_called_once_with(self.auth_user.email)

    def test_elrr_get_or_create_elrr_person_by_email_new_user(self):
        """Test get or create a person in ELRR by email for new user"""
        person_id = '999-888-777-666'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with (patch('external.utils.elrr_utils.get_elrr_person_id_by_email')
              as get_mock):
            with (patch('external.utils.elrr_utils.create_elrr_person')
                  as create_mock):
                get_mock.return_value = None
                create_mock.return_value = person_id

                actual = get_or_create_elrr_person_by_email(self.auth_user)

                self.assertEqual(actual, person_id)
                get_mock.assert_called_once_with(self.auth_user.email)
                create_mock.assert_called_once_with(self.auth_user)

    def test_elrr_calculate_goal_achieved_by_date_months(self):
        """Test calculation of goal achieved by date (months)"""
        start_date = timezone.now()
        timeline = '3-6 months'

        actual_date = calculate_goal_achieved_by_date(start_date,
                                                      timeline)

        expected_months = 6

        delta_date = relativedelta(actual_date, start_date)
        month_diff = delta_date.years * 12 + delta_date.months

        self.assertEqual(month_diff, expected_months)

    def test_elrr_calculate_goal_achieved_by_date_years(self):
        """Test calculation of goal achieved by date (years)"""
        start_date = timezone.now()
        timeline = '2-2.5 years'

        actual_date = calculate_goal_achieved_by_date(start_date,
                                                      timeline)

        expected_months = 30

        delta_date = relativedelta(actual_date, start_date)
        month_diff = delta_date.years * 12 + delta_date.months

        self.assertEqual(month_diff, expected_months)

    def test_elrr_calculate_goal_achieved_by_date_no_timeline(self):
        """Test calculation of goal achieved by date with no timeline"""
        start_date = timezone.now()
        timeline = None

        actual_date = calculate_goal_achieved_by_date(start_date,
                                                      timeline)

        self.assertIsNone(actual_date)

    def test_elrr_get_elrr_goal(self):
        """Test getting elrr goal by id"""
        goal_id = 'test-goal-id-998'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()
        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {
                'id': goal_id,
                'name': 'Test Goal Nine',
            }
            req.get.return_value = resp

            actual = get_elrr_goal(goal_id)

            self.assertEqual(actual['id'], goal_id)
            req.get.assert_called_once()

    def test_elrr_create_elrr_goal(self):
        """Test creating elrr goal"""
        goal_id = 'test-new-goal-111'
        person_id = '333-444-555-666'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        goal_data = {
            'personId': person_id,
            'name': 'New Goal 998',
            'type': 'SELF',
        }

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 201
            resp.json.return_value = {
                'id': goal_id,
                'name': goal_data['name'],
                'type': goal_data['type'],
            }
            req.post.return_value = resp

            actual = create_elrr_goal(goal_data)

            self.assertEqual(actual['id'], goal_id)
            req.post.assert_called_once()

    def test_elrr_update_elrr_goal(self):
        """Test updating elrr goal"""
        goal_id = 'test-update-goal-555'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        goal_data = {
            'id': goal_id,
            'name': 'Updated Test Goal Name',
        }

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = goal_data
            req.put.return_value = resp

            actual = update_elrr_goal(goal_data)

            self.assertEqual(actual['id'], goal_id)
            req.put.assert_called_once()

    def test_elrr_remove_elrr_goal(self):
        """Test removing elrr goal"""
        goal_id = 'test-remove-goal-777'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 204
            req.delete.return_value = resp

            actual = remove_goal_from_elrr(goal_id)
            self.assertTrue(actual)
            req.delete.assert_called_once()

    def test_get_or_create_elrr_competency_exisiting(self):
        """Test get or create elrr competency"""
        competency_id = 'test-comp-123-456'
        reference = 'testFramework/9988'
        name = 'Test Competency 9988'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = [{
                'id': competency_id,
                'identifier': reference,
                'statement': name
            }]
            req.get.return_value = resp

            actual = get_or_create_elrr_competency(reference, name)
            self.assertEqual(actual['id'], competency_id)
            req.get.assert_called_once()

    def test_get_or_create_elrr_competency_new(self):
        """Test get or create elrr competency when new"""
        competency_id = 'test-comp-897-543'
        reference = 'newFramework/1122'
        name = 'New Competency 1122'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp_get = Mock()
            resp_get.status_code = 200
            resp_get.json.return_value = []

            resp_post = Mock()
            resp_post.status_code = 201
            resp_post.json.return_value = {
                'id': competency_id,
                'identifier': reference,
                'statement': name
            }

            req.get.return_value = resp_get
            req.post.return_value = resp_post

            actual = get_or_create_elrr_competency(reference, name)
            self.assertEqual(actual['id'], competency_id)

            req.get.assert_called_once()
            req.post.assert_called_once()

    def test_get_or_create_elrr_learning_resource_existing(self):
        """Test get or create elrr learning resource when existing"""
        lr_id = 'test-lr-123-456'
        reference = '1239004223'
        name = 'Test Learning Resource 9988'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = [{
                'id': lr_id,
                'identifier': reference,
                'title': name
            }]
            req.get.return_value = resp

            actual = get_or_create_elrr_learning_resource(reference, name)

            self.assertEqual(actual['id'], lr_id)
            req.get.assert_called_once()

    def test_get_or_create_elrr_learning_resource_new(self):
        """Test get or create elrr learning resource when new"""
        lr_id = 'test-lr-897-543'
        reference = '5566778899'
        name = 'New Learning Resource 1122'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.requests') as req:
            resp_get = Mock()
            resp_get.status_code = 200
            resp_get.json.return_value = []

            resp_post = Mock()
            resp_post.status_code = 201
            resp_post.json.return_value = {
                'id': lr_id,
                'identifier': reference,
                'title': name
            }

            req.get.return_value = resp_get
            req.post.return_value = resp_post

            actual = get_or_create_elrr_learning_resource(reference, name)
            self.assertEqual(actual['id'], lr_id)

            req.get.assert_called_once()
            req.post.assert_called_once()

    def test_elrr_remove_ksa_from_elrr_goal(self):
        """Test removing ksa from elrr goal"""
        goal_id = 'test-goal-ksa-111'
        comp_id = 'test-compe-ksa-222'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.get_elrr_goal') as get_mock:
            with (patch('external.utils.elrr_utils.update_elrr_goal')
                  as update_mock):
                goal_data = {
                    'id': goal_id,
                    'competencyIds': [comp_id]
                }

                get_mock.return_value = goal_data
                remove_ksa_from_elrr_goal(goal_id, comp_id)

                self.assertNotIn(comp_id, goal_data['competencyIds'])
                get_mock.assert_called_once_with(goal_id)
                update_mock.assert_called_once_with(goal_data)

    def test_elrr_remove_course_from_elrr_goal(self):
        """Test removing course from elrr goal"""
        goal_id = 'test-goal-course-333'
        lr_id = 'test-lr-course-444'
        elrr_api = 'https://elrr-example.com'
        conf = Configuration(target_elrr_api=elrr_api,
                             target_elrr_api_key='test_token_998')
        conf.save()

        with patch('external.utils.elrr_utils.get_elrr_goal') as get_mock:
            with (patch('external.utils.elrr_utils.update_elrr_goal')
                  as update_mock):
                goal_data = {
                    'id': goal_id,
                    'learningResourceIds': [lr_id]
                }

                get_mock.return_value = goal_data
                remove_course_from_elrr_goal(goal_id, lr_id)

                self.assertNotIn(lr_id, goal_data['learningResourceIds'])
                get_mock.assert_called_once_with(goal_id)
                update_mock.assert_called_once_with(goal_data)
