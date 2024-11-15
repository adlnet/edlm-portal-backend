from django.test import override_settings
from rest_framework.test import APITestCase

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse, TrainingPlan)
from external.models import Job
from users.models import User
from vacancies.models import Vacancy


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in EDLM Portal"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        # settings management
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

        # Auth stuff
        self.auth_email = "test_auth@test.com"
        self.auth_password = "test_auth1234"
        self.auth_first_name = "first_name_auth"
        self.auth_last_name = "last_name_auth"

        User.objects.create_user(self.auth_email,
                                 email=self.auth_email,
                                 password=self.auth_password,
                                 first_name=self.auth_first_name,
                                 last_name=self.auth_last_name,
                                 is_superuser=True)
        self.auth_user = User.objects.get(username=self.auth_email)

        self.basic_email = "test_basic@test.com"
        self.basic_password = "test_basic1234"
        self.basic_first_name = "first_name_basic"
        self.basic_last_name = "last_name_basic"

        User.objects.create_user(self.basic_email,
                                 email=self.basic_email,
                                 password=self.basic_password,
                                 first_name=self.basic_first_name,
                                 last_name=self.basic_last_name,
                                 is_superuser=True)
        self.basic_user = User.objects.get(username=self.basic_email)

        # Profile Question
        active = True
        order = 32
        question = "What color is the sky?"

        self.pq = ProfileQuestion(active=active,
                                  order=order,
                                  question=question)

        # Profile Answer
        order = 32
        answer = "Blue"

        self.pa = ProfileAnswer(question=self.pq,
                                order=order,
                                answer=answer)
        order_2 = 13
        answer_2 = "Green"

        self.pa_2 = ProfileAnswer(question=self.pq,
                                  order=order_2,
                                  answer=answer_2)

        # Profile Response
        self.pr = ProfileResponse(question=self.pq,
                                  submitted_by=self.auth_user,
                                  selected=self.pa)

        # Job
        name = "it"
        ref = "abc123"
        job_type = "cyber"
        self.job = Job(name=name,
                       reference=ref,
                       job_type=job_type)

        # Candidate List
        name = 'my cl'
        self.cl = CandidateList(name=name,
                                ranker=self.auth_user,
                                competency=self.job)

        # Candidate Ranking
        rank = 16

        self.cr = CandidateRanking(candidate_list=self.cl,
                                   candidate=self.auth_user,
                                   rank=rank)

        # Training Plan
        self.tp = TrainingPlan(trainee=self.basic_user,
                               planner=self.auth_user,
                               role=self.job)

        return super().setUp()
