from django.test import override_settings
from rest_framework.test import APITestCase

from api.models import (CandidateList, CandidateRanking, LearningPlan,
                        LearningPlanCompetency, LearningPlanGoal,
                        LearningPlanGoalCourse, LearningPlanGoalKsa,
                        ProfileAnswer, ProfileQuestion,
                        ProfileResponse, TrainingPlan, Application)
from configuration.models import Configuration
from external.models import Competency, Course, Job, Ksa
from users.models import User


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

        # Learning Plan
        name = "Test Learning Plan"
        timeframe = "Short-term (1-2 years)"
        self.learning_plan = LearningPlan(
            learner=self.auth_user,
            name=name,
            timeframe=timeframe
        )

        # Learning Plan Competency
        name = "Test Competency"
        reference = "http://test.example.com/testframework/111"
        self.competency = Competency(
            name=name,
            reference=reference
        )

        priority = "High"
        self.learning_plan_competency = LearningPlanCompetency(
            learning_plan=self.learning_plan,
            eccr_competency=self.competency,
            priority=priority
        )

        # Learning Plan Goal
        goal_name = "Test Goal"
        timeline = 3
        resources_support = ["test_resource1", "test_resource2"]
        obstacles = ["test_obstacle1", "test_obstacle2"]
        resources_support_other = "Other test resource"
        obstacles_other = "Other test obstacle"
        self.learning_plan_goal = LearningPlanGoal(
            plan_competency=self.learning_plan_competency,
            goal_name=goal_name,
            timeline=timeline,
            resources_support=resources_support,
            obstacles=obstacles,
            resources_support_other=resources_support_other,
            obstacles_other=obstacles_other
        )

        # Learning Plan Goal KSA
        name = "Test KSA"
        reference = "http://test.example.com/testframework/ksa/111"
        self.ksa = Ksa(
            name=name,
            reference=reference
        )

        current_proficiency = "test_low"
        target_proficiency = "test_medium"
        self.learning_plan_goal_ksa = LearningPlanGoalKsa(
            plan_goal=self.learning_plan_goal,
            eccr_ksa=self.ksa,
            current_proficiency=current_proficiency,
            target_proficiency=target_proficiency
        )

        # Learning Plan Goal Course
        course_name = "Test Course"
        reference = "abcdefg12345"
        self.course = Course(
            name=course_name,
            reference=reference
        )

        self.learning_plan_goal_course = LearningPlanGoalCourse(
            plan_goal=self.learning_plan_goal,
            xds_course=self.course
        )

        # Application
        applicant = self.basic_user
        app_first_name = "John"
        app_last_name = "Doe"
        code_of_ethics_acknowledgement = True
        app_status = Application.StatusChoices.DRAFT
        application_type = Application.ApplicationChoices.NEW

        self.application = Application(
            applicant=applicant,
            first_name=app_first_name,
            last_name=app_last_name,
            code_of_ethics_acknowledgement=code_of_ethics_acknowledgement,
            status=app_status,
            application_type=application_type,
        )

        # Configuration
        self.config = Configuration(
            target_xds_api="test-xds",
            target_elrr_api="test-elrr",
            target_eccr_api="test-eccr",
            target_xms_api="test-xms",
            target_ldss_api="test-ldss",
            lrs_endpoint="http://lrs.example.com/xapi",
            lrs_username="username",
            lrs_password="testpass"
        ).save()

        return super().setUp()
