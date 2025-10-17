import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from rest_framework import status

from .test_setup import TestSetUp

API_PROFILE_QUESTIONS_DETAIL = 'api:profile-questions-detail'
API_PROFILE_RESPONSES_DETAIL = 'api:profile-responses-detail'
API_CANDIDATE_LISTS_DETAIL = 'api:candidate-lists-detail'
API_CANDIDATE_RANKINGS_DETAIL = 'api:candidate-rankings-detail'
API_TRAINING_PLANS_DETAIL = 'api:training-plans-detail'
API_LEARNING_PLANS_DETAIL = 'api:learning-plans-detail'
API_LEARNING_PLAN_COMPETENCIES_DETAIL = 'api:learning-plan-competencies-detail'
API_LEARNING_PLAN_GOALS_DETAIL = 'api:learning-plan-goals-detail'
API_LEARNING_PLAN_GOAL_KSAS_DETAIL = 'api:learning-plan-goal-ksas-detail'
EXPECTED_ERROR = "Authentication credentials were not provided."


@tag('unit')
class ViewTests(TestSetUp):

    def test_profile_question_requests_no_auth(self):
        """Test that making a get request to the profile question api with no
        auth returns an error"""
        url = reverse(API_PROFILE_QUESTIONS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_question_requests_bad_id(self):
        """Test that making a get request to the profile question api with a
        bad id returns an error"""
        url = reverse(API_PROFILE_QUESTIONS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No ProfileQuestion matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_question_requests_pass(self):
        """Test that making a get request to the profile question api with a
        correct id returns the profile question"""
        self.pq.save()
        self.pa.save()
        self.pa_2.save()
        url = reverse(API_PROFILE_QUESTIONS_DETAIL,
                      kwargs={"pk": self.pq.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.pq.order, responseDict['order'])
        self.assertEqual(self.pq.question, responseDict['question'])
        self.assertEqual(self.pq.pk, responseDict['id'])
        self.assertEqual(self.pq.answers.count(), len(responseDict['answers']))

    def test_profile_response_requests_no_auth(self):
        """Test that making a get request to the profile response api with no
        auth returns an error"""
        url = reverse(API_PROFILE_RESPONSES_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_response_requests_bad_id(self):
        """Test that making a get request to the profile response api with a
        bad id returns an error"""
        url = reverse(API_PROFILE_RESPONSES_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No ProfileResponse matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_response_requests_pass(self):
        """Test that making a get request to the profile response api with a
        correct id returns the profile response"""
        self.pq.save()
        self.pa.save()
        self.pa_2.save()
        self.pr.save()
        url = reverse(API_PROFILE_RESPONSES_DETAIL,
                      kwargs={"pk": self.pr.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.pr.selected.pk, responseDict['selected'])
        self.assertEqual(self.pr.question.pk, responseDict['question'])
        self.assertEqual(self.pr.pk, responseDict['id'])
        self.assertEqual(self.pr.submitted_by.email,
                         responseDict['submitted_by'])

    def test_profile_response_requests_post(self):
        """Test that making a post request to the profile response api with
        valid data creates a profile response"""
        self.pq.save()
        self.pa.save()
        self.pa_2.save()
        url = reverse('api:profile-responses-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'question': self.pr.question.pk,
                  'selected': self.pr.selected.pk,
                  'submitted_by': "anyone"})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.pr.selected.pk, responseDict['selected'])
        self.assertEqual(self.pr.question.pk, responseDict['question'])
        self.assertIsNotNone(responseDict['id'])
        self.assertEqual(self.pr.submitted_by.email,
                         responseDict['submitted_by'])

    def test_candidate_list_requests_no_auth(self):
        """Test that making a get request to the candidate list api with no
        auth returns an error"""
        url = reverse(API_CANDIDATE_LISTS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_list_requests_bad_id(self):
        """Test that making a get request to the candidate list api with a
        bad id returns an error"""
        url = reverse(API_CANDIDATE_LISTS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No CandidateList matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_list_requests_pass(self):
        """Test that making a get request to the candidate list api with a
        correct id returns the candidate list"""
        self.job.save()
        self.cl.save()
        url = reverse(API_CANDIDATE_LISTS_DETAIL,
                      kwargs={"pk": self.cl.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cl.competency.pk, responseDict['competency'])
        self.assertEqual(self.cl.name, responseDict['name'])
        self.assertEqual(self.cl.pk, responseDict['id'])
        self.assertEqual(self.cl.ranker.email,
                         responseDict['ranker'])

    def test_candidate_list_requests_post(self):
        """Test that making a post request to the candidate list api with
        valid data creates a candidate list"""
        self.job.save()
        name = "some cl"
        url = reverse('api:candidate-lists-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'name': name,
                  'competency': self.job.pk,
                  'ranker': "anyone"})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(name, responseDict['name'])
        self.assertEqual(self.job.pk, responseDict['competency'])
        self.assertIsNotNone(responseDict['id'])
        self.assertEqual(self.auth_user.email,
                         responseDict['ranker'])

    def test_candidate_ranking_requests_no_auth(self):
        """Test that making a get request to the candidate ranking api with no
        auth returns an error"""
        url = reverse(API_CANDIDATE_RANKINGS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_ranking_requests_bad_id(self):
        """Test that making a get request to the candidate ranking api with a
        bad id returns an error"""
        url = reverse(API_CANDIDATE_RANKINGS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No CandidateRanking matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_ranking_requests_pass(self):
        """Test that making a get request to the candidate ranking api with a
        correct id returns the candidate ranking"""
        self.job.save()
        self.cl.save()
        self.cr.save()

        url = reverse(API_CANDIDATE_RANKINGS_DETAIL,
                      kwargs={"pk": self.cr.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cr.candidate.email, responseDict['candidate'])
        self.assertEqual(self.cr.candidate_list.pk,
                         responseDict['candidate_list'])
        self.assertEqual(self.cr.pk, responseDict['id'])
        self.assertEqual(self.cr.rank, responseDict['rank'])

    def test_candidate_ranking_requests_post(self):
        """Test that making a post request to the candidate ranking api with
        valid data creates a candidate ranking"""
        self.job.save()
        self.cl.save()
        rank = 42
        url = reverse('api:candidate-rankings-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'rank': rank,
                  'candidate_list': self.cl.pk,
                  'candidate': self.basic_email})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rank, responseDict['rank'])
        self.assertEqual(self.cl.pk, responseDict['candidate_list'])
        self.assertIsNotNone(responseDict['id'])
        self.assertEqual(self.basic_user.email,
                         responseDict['candidate'])

    def test_training_plan_requests_no_auth(self):
        """Test that making a get request to the training plan api with no
        auth returns an error"""
        url = reverse(API_TRAINING_PLANS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_training_plan_requests_bad_id(self):
        """Test that making a get request to the training plan api with a
        bad id returns an error"""
        url = reverse(API_TRAINING_PLANS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No TrainingPlan matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_training_plan_requests_pass(self):
        """Test that making a get request to the training plan api with a
        correct id returns the training plan"""
        self.job.save()
        self.tp.save()

        url = reverse(API_TRAINING_PLANS_DETAIL,
                      kwargs={"pk": self.tp.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.tp.trainee.email, responseDict['trainee'])
        self.assertEqual(self.tp.role.pk,
                         responseDict['role'])
        self.assertEqual(self.tp.pk, responseDict['id'])
        self.assertEqual(self.tp.planner.email, responseDict['planner'])

    def test_training_plan_requests_post(self):
        """Test that making a post request to the training plan api with
        valid data creates a training plan"""
        self.job.save()

        url = reverse('api:training-plans-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'role': self.job.pk,
                  'trainee': self.basic_user.email,
                  'planner': "anyone"})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.auth_user.email, responseDict['planner'])
        self.assertEqual(self.job.pk, responseDict['role'])
        self.assertIsNotNone(responseDict['id'])
        self.assertEqual(self.basic_user.email,
                         responseDict['trainee'])

    def test_learning_plan_requests_no_auth(self):
        """Test that making a get request to the learning plan api with no
        auth returns an error"""
        url = reverse(API_LEARNING_PLANS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_requests_bad_id(self):
        """Test that making a get request to the learning plan api with a
        bad id returns an error"""
        url = reverse(API_LEARNING_PLANS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No LearningPlan matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_requests_pass(self):
        """Test that making a get request to the learning plan api with a
        correct id returns the learning plan"""
        self.learning_plan.save()

        url = reverse(API_LEARNING_PLANS_DETAIL,
                      kwargs={"pk": self.learning_plan.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.learning_plan.learner.email,
                         responseDict['learner'])
        self.assertEqual(self.learning_plan.timeframe,
                         responseDict['timeframe'])
        self.assertEqual(self.learning_plan.pk, responseDict['id'])
        self.assertEqual(self.learning_plan.timeframe,
                         responseDict['timeframe'])

    def test_learning_plan_requests_post(self):
        """Test that making a post request to the learning plan api with
        valid data creates a learning plan"""
        url = reverse('api:learning-plans-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'name': self.learning_plan.name,
                  'timeframe': self.learning_plan.timeframe,
                  'learner': self.basic_email})

        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.learning_plan.name, responseDict['name'])
        self.assertEqual(self.learning_plan.timeframe,
                         responseDict['timeframe'])
        self.assertIsNotNone(responseDict['id'])
        self.assertEqual(self.basic_user.email,
                         responseDict['learner'])

    def test_learning_plan_competency_requests_no_auth(self):
        """Test that making a get request to the learning plan
        competency api with no auth returns an error"""
        url = reverse(API_LEARNING_PLAN_COMPETENCIES_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_competency_requests_bad_id(self):
        """Test that making a get request to the learning plan
        competency api with a bad id returns an error"""
        url = reverse(API_LEARNING_PLAN_COMPETENCIES_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No LearningPlanCompetency matches the given query."
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_competency_requests_pass(self):
        """Test that making a get request to the learning plan competency
        api with a correct id returns the learning plan competency"""
        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()

        url = reverse(API_LEARNING_PLAN_COMPETENCIES_DETAIL,
                      kwargs={"pk": self.learning_plan_competency.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.learning_plan_competency.learning_plan.pk,
                         responseDict['learning_plan'])
        self.assertEqual(self.learning_plan_competency.pk, responseDict['id'])
        self.assertEqual(self.learning_plan_competency.priority,
                         responseDict['priority'])

    @patch('api.serializers.get_eccr_item')
    def test_learning_plan_competency_requests_post(self, mock_eccr):
        """Test that making a post request to the learning plan competency
        api with valid data creates a learning plan competency"""
        mock_eccr.return_value.status_code = 200
        mock_eccr.return_value.json.return_value = {
            "test": "test1"
        }

        self.learning_plan.save()
        priority = "Low"
        com_name = "test competency"
        comp_ref = "testFramework/test-uuid"

        url = reverse('api:learning-plan-competencies-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'learning_plan': self.learning_plan.pk,
                  'priority': priority,
                  'competency_external_name': com_name,
                  'competency_external_reference': comp_ref})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(priority, responseDict['priority'])
        self.assertEqual(self.learning_plan.pk, responseDict['learning_plan'])
        self.assertEqual(com_name, responseDict['plan_competency_name'])
        self.assertIsNotNone(responseDict['id'])

    def test_learning_plan_goal_requests_no_auth(self):
        """Test that making a get request to the learning plan goal api with no
        auth returns an error"""
        url = reverse(API_LEARNING_PLAN_GOALS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_goal_requests_bad_id(self):
        """Test that making a get request to the learning plan goal api with a
        bad id returns an error"""
        url = reverse(API_LEARNING_PLAN_GOALS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No LearningPlanGoal matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_goal_requests_pass(self):
        """Test that making a get request to the learning plan goal api with a
        correct id returns the learning plan goal"""
        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        self.learning_plan_goal.save()

        url = reverse(API_LEARNING_PLAN_GOALS_DETAIL,
                      kwargs={"pk": self.learning_plan_goal.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.learning_plan_goal.plan_competency.pk,
                         responseDict['plan_competency'])
        self.assertEqual(self.learning_plan_goal.pk, responseDict['id'])
        self.assertEqual(self.learning_plan_goal.timeline,
                         responseDict['timeline'])

    def test_learning_plan_goal_requests_post(self):
        """Test that making a post request to the learning plan goal api with
        valid data creates a learning plan goal"""
        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        timeline = "3 months"
        goal_name = "test goal"

        url = reverse('api:learning-plan-goals-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'plan_competency': self.learning_plan_competency.pk,
                  'timeline': timeline,
                  'goal_name': goal_name})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(timeline, responseDict['timeline'])
        self.assertEqual(goal_name, responseDict['goal_name'])
        self.assertEqual(self.learning_plan_competency.pk,
                         responseDict['plan_competency'])
        self.assertIsNotNone(responseDict['id'])

    def test_learning_plan_goal_ksa_requests_no_auth(self):
        """Test that making a get request to the learning
        plan goal ksa api with no auth returns an error"""
        url = reverse(API_LEARNING_PLAN_GOAL_KSAS_DETAIL, kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = EXPECTED_ERROR

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_goal_ksa_requests_bad_id(self):
        """Test that making a get request to the learning plan
        goal ksa api with a bad id returns an error"""
        url = reverse(API_LEARNING_PLAN_GOAL_KSAS_DETAIL, kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No LearningPlanGoalKsa matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_learning_plan_goal_ksa_requests_pass(self):
        """Test that making a get request to the learning plan goal
        ksa api with a correct id returns the learning plan goal ksa"""
        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        self.learning_plan_goal.save()
        self.ksa.save()
        self.learning_plan_goal_ksa.save()

        url = reverse(API_LEARNING_PLAN_GOAL_KSAS_DETAIL,
                      kwargs={"pk": self.learning_plan_goal_ksa.pk})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.learning_plan_goal_ksa.plan_goal.pk,
                         responseDict['plan_goal'])
        self.assertEqual(self.learning_plan_goal_ksa.pk, responseDict['id'])
        self.assertEqual(self.learning_plan_goal_ksa.current_proficiency,
                         responseDict['current_proficiency'])

    @patch('api.serializers.get_eccr_item')
    def test_learning_plan_goal_ksa_requests_post(self, mock_eccr):
        """Test that making a post request to the learning plan
        goal ksa api with valid data creates a learning plan goal ksa"""
        mock_eccr.return_value.status_code = 200
        mock_eccr.return_value.json.return_value = {
            "test": "test2"
        }

        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        self.learning_plan_goal.save()

        current_proficiency = "Intermediate"
        target_proficiency = "Advanced"
        ksa_name = "test ksa"
        ksa_reference = "framework1/ksa-uuid-test"

        url = reverse('api:learning-plan-goal-ksas-list')
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.post(
            url, {'plan_goal': self.learning_plan_goal.pk,
                  'current_proficiency': current_proficiency,
                  'target_proficiency': target_proficiency,
                  'ksa_external_name': ksa_name,
                  'ksa_external_reference': ksa_reference})
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_proficiency,
                         responseDict['current_proficiency'])
        self.assertEqual(target_proficiency,
                         responseDict['target_proficiency'])
        self.assertEqual(self.learning_plan_goal.pk,
                         responseDict['plan_goal'])
        self.assertEqual(ksa_name, responseDict['ksa_name'])
        self.assertIsNotNone(responseDict['id'])


@tag("unit")
class GetCourseProgressViewTests(TestSetUp):
    @patch("api.views.get_lrs_statements")
    def test_get_lrs_success(self, mock_get_lrs):
        """Test that LRS data are retrieved successfully"""
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        mock_get_lrs.return_value = {
            "statements": []
        }

        url = reverse("api:course_progress")

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @patch("api.views.get_lrs_statements",
           side_effect=Exception("Unexpected Error")
           )
    def test_return_general_error(self, mock_get_lrs):
        """Test that returns an unexpected general error occurs"""
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        mock_get_lrs.return_value = {
            "statements": []
        }

        url = reverse("api:course_progress")

        resp = self.client.get(url)

        self.assertEqual(
            resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @patch("api.views.get_lrs_statements",
           side_effect=ConnectionError("Connection failed")
           )
    def test_returns_502_when_connection_fails(self, mock_get_lrs):
        """Test that returns a 502 error when the connection fails"""
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        url = reverse("api:course_progress")

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
