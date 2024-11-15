import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from rest_framework import status

from external.models import Job
from users.models import User

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_profile_question_requests_no_auth(self):
        """Test that making a get request to the profile question api with no
        auth returns an error"""
        url = reverse('api:profile-questions-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_question_requests_bad_id(self):
        """Test that making a get request to the profile question api with a
        bad id returns an error"""
        url = reverse('api:profile-questions-detail', kwargs={"pk": 1})
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
        url = reverse('api:profile-questions-detail',
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
        url = reverse('api:profile-responses-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_response_requests_bad_id(self):
        """Test that making a get request to the profile response api with a
        bad id returns an error"""
        url = reverse('api:profile-responses-detail', kwargs={"pk": 1})
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
        url = reverse('api:profile-responses-detail',
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
        url = reverse('api:candidate-lists-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_list_requests_bad_id(self):
        """Test that making a get request to the candidate list api with a
        bad id returns an error"""
        url = reverse('api:candidate-lists-detail', kwargs={"pk": 1})
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
        url = reverse('api:candidate-lists-detail',
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
        url = reverse('api:candidate-rankings-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_candidate_ranking_requests_bad_id(self):
        """Test that making a get request to the candidate ranking api with a
        bad id returns an error"""
        url = reverse('api:candidate-rankings-detail', kwargs={"pk": 1})
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

        url = reverse('api:candidate-rankings-detail',
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
        url = reverse('api:training-plans-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_training_plan_requests_bad_id(self):
        """Test that making a get request to the training plan api with a
        bad id returns an error"""
        url = reverse('api:training-plans-detail', kwargs={"pk": 1})
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

        url = reverse('api:training-plans-detail',
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
