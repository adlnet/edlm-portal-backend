from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.test import tag

from api.models import (CandidateList, CandidateRanking, LearningPlan,
                        LearningPlanCompetency, LearningPlanGoal,
                        LearningPlanGoalCourse, LearningPlanGoalKsa,
                        ProfileAnswer, ProfileQuestion,
                        ProfileResponse, Application, ApplicationComment,
                        ApplicationCourse, ApplicationExperience)

from .test_setup import TestSetUp

SKY_COLOR = "What color is the sky?"
ERROR_MSG_VALUE = " to 0.']}"


@tag('unit')
class ModelTests(TestSetUp):

    def test_profile_question(self):
        """Test that creating a ProfileQuestion is successful"""

        active = True
        order = 32
        question = SKY_COLOR

        pq = ProfileQuestion(active=active,
                             order=order,
                             question=question)
        pq.full_clean()
        pq.save()

        self.assertEqual(pq.active, active)
        self.assertEqual(pq.order, order)
        self.assertEqual(pq.question, question)
        self.assertEqual(str(pq), f'{order}. {question}')
        self.assertEqual(ProfileQuestion.objects.all().count(), 1)
        self.assertIn(str(pq.pk), pq.get_absolute_url())

    def test_profile_question_bad_order(self):
        """Test that creating a ProfileQuestion with a wrong order fails"""

        active = True
        order = -32
        question = SKY_COLOR
        error_msg = "{'order': ['Ensure this value is greater than or equal" +\
            ERROR_MSG_VALUE

        pq = ProfileQuestion(active=active,
                             order=order,
                             question=question)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pq.full_clean)
        self.assertEqual(ProfileQuestion.objects.all().count(), 0)

    def test_profile_question_non_unique_order(self):
        """Test that creating a ProfileQuestion with a non unique order fails
        """

        active = True
        order = 32
        question = SKY_COLOR
        question_2 = "What color is the ground?"
        error_msg = "{'order': ['Profile question with this Order already" +\
            " exists.']}"

        pq = ProfileQuestion(active=active,
                             order=order,
                             question=question)
        pq.full_clean()
        pq.save()

        pq_2 = ProfileQuestion(active=active,
                               order=order,
                               question=question_2)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pq_2.full_clean)
        self.assertEqual(ProfileQuestion.objects.all().count(), 1)

    def test_profile_question_non_unique_question(self):
        """Test that creating a ProfileQuestion with a non unique question
        fails"""

        active = True
        order = 32
        order_2 = 13
        question = SKY_COLOR
        error_msg = "{'question': ['Profile question with this Question " + \
            "already exists.']}"

        pq = ProfileQuestion(active=active,
                             order=order,
                             question=question)
        pq.full_clean()
        pq.save()

        pq_2 = ProfileQuestion(active=active,
                               order=order_2,
                               question=question)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pq_2.full_clean)
        self.assertEqual(ProfileQuestion.objects.all().count(), 1)

    def test_profile_answer(self):
        """Test that creating a ProfileAnswer is successful"""

        self.pq.save()
        order = 32
        answer = "Blue"

        pa = ProfileAnswer(question=self.pq,
                           order=order,
                           answer=answer)
        pa.full_clean()
        pa.save()

        self.assertEqual(pa.order, order)
        self.assertEqual(pa.answer, answer)
        self.assertEqual(str(pa), f'{order}. {answer}')
        self.assertEqual(ProfileAnswer.objects.all().count(), 1)
        self.assertEqual(self.pq.answers.count(), 1)

    def test_profile_answer_bad_order(self):
        """Test that creating a ProfileAnswer with a wrong order fails"""

        self.pq.save()
        order = -32
        answer = "Blue"
        error_msg = "{'order': ['Ensure this value is greater than or equal" +\
            ERROR_MSG_VALUE

        pa = ProfileAnswer(question=self.pq,
                           order=order,
                           answer=answer)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pa.full_clean)
        self.assertEqual(ProfileAnswer.objects.all().count(), 0)
        self.assertEqual(self.pq.answers.count(), 0)

    def test_profile_answer_non_unique_order(self):
        """Test that creating a ProfileAnswer with a non unique order fails"""

        self.pq.save()
        order = 32
        answer = "Blue"
        answer_2 = "Green"
        error_msg = "{'__all__': ['Profile answer with this Question and " +\
            "Order already exists.']}"

        pa = ProfileAnswer(question=self.pq,
                           order=order,
                           answer=answer)
        pa.full_clean()
        pa.save()

        pa_2 = ProfileAnswer(question=self.pq,
                             order=order,
                             answer=answer_2)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pa_2.full_clean)
        self.assertEqual(ProfileAnswer.objects.all().count(), 1)
        self.assertEqual(self.pq.answers.count(), 1)

    def test_profile_answer_non_unique_answer(self):
        """Test that creating a ProfileAnswer with a non unique answer fails"""

        self.pq.save()
        order = 32
        order_2 = 3
        answer = "Blue"
        error_msg = "{'__all__': ['Profile answer with this Question and " +\
            "Answer already exists.']}"

        pa = ProfileAnswer(question=self.pq,
                           order=order,
                           answer=answer)
        pa.full_clean()
        pa.save()

        pa_2 = ProfileAnswer(question=self.pq,
                             order=order_2,
                             answer=answer)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pa_2.full_clean)
        self.assertEqual(ProfileAnswer.objects.all().count(), 1)
        self.assertEqual(self.pq.answers.count(), 1)

    def test_profile_response(self):
        """Test that creating a ProfileResponse is successful"""

        self.pq.save()
        self.pa.save()

        pr = ProfileResponse(question=self.pq,
                             submitted_by=self.auth_user,
                             selected=self.pa)
        pr.full_clean()
        pr.save()

        self.assertEqual(pr.question, self.pq)
        self.assertEqual(pr.selected, self.pa)
        self.assertEqual(pr.submitted_by, self.auth_user)
        self.assertEqual(ProfileResponse.objects.all().count(), 1)
        self.assertEqual(self.pq.responses.count(), 1)
        self.assertEqual(self.pa.responses.count(), 1)
        self.assertEqual(self.auth_user.responses.count(), 1)
        self.assertIn(str(pr.pk), pr.get_absolute_url())

    def test_profile_response_non_unique_question(self):
        """Test that creating a ProfileResponse with a non unique question
        fails"""

        self.pq.save()
        self.pa.save()
        self.pa_2.save()
        error_msg = "{'__all__': ['Profile response with this Question and " +\
            "Submitted by already exists.']}"

        pr = ProfileResponse(question=self.pq,
                             submitted_by=self.auth_user,
                             selected=self.pa)
        pr.full_clean()
        pr.save()

        pr_2 = ProfileResponse(question=self.pq,
                               submitted_by=self.auth_user,
                               selected=self.pa_2)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 pr_2.full_clean)
        self.assertEqual(ProfileResponse.objects.all().count(), 1)
        self.assertEqual(self.pq.responses.count(), 1)
        self.assertEqual(self.pa.responses.count(), 1)
        self.assertEqual(self.auth_user.responses.count(), 1)

    def test_candidate_list(self):
        """Test that creating a CandidateList is successful"""

        name = 'my cl'
        self.job.save()

        cl = CandidateList(name=name,
                           ranker=self.auth_user,
                           competency=self.job)
        cl.full_clean()
        cl.save()

        self.assertEqual(cl.name, name)
        self.assertEqual(cl.ranker, self.auth_user)
        self.assertEqual(cl.competency, self.job)
        self.assertIn(name, str(cl))
        self.assertIn(str(self.job), str(cl))
        self.assertIn(str(self.auth_user), str(cl))
        self.assertEqual(CandidateList.objects.all().count(), 1)
        self.assertEqual(self.job.recommended.count(), 1)
        self.assertEqual(self.auth_user.lists.count(), 1)
        self.assertIn(str(cl.pk), cl.get_absolute_url())

    def test_candidate_list_missing_role_and_competency(self):
        """Test that creating a CandidateList with missing role and competency
        fails"""

        name = 'my cl'
        error_msg = "{'__all__': ['Constraint “role_or_competency” is " +\
            "violated.']}"

        cl = CandidateList(name=name,
                           ranker=self.auth_user)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 cl.full_clean)
        self.assertEqual(CandidateList.objects.all().count(), 0)
        self.assertEqual(self.job.recommended.count(), 0)
        self.assertEqual(self.auth_user.lists.count(), 0)

    def test_candidate_ranking(self):
        """Test that creating a CandidateRanking is successful"""

        rank = 16
        self.job.save()
        self.cl.save()

        cr = CandidateRanking(candidate_list=self.cl,
                              candidate=self.auth_user,
                              rank=rank)
        cr.full_clean()
        cr.save()

        self.assertEqual(cr.rank, rank)
        self.assertEqual(cr.candidate, self.auth_user)
        self.assertEqual(cr.candidate_list, self.cl)
        self.assertIn(str(rank), str(cr))
        self.assertIn(str(self.cl), str(cr))
        self.assertIn(str(self.auth_user), str(cr))
        self.assertEqual(CandidateRanking.objects.all().count(), 1)
        self.assertEqual(self.cl.rankings.count(), 1)
        self.assertEqual(self.auth_user.rankings.count(), 1)
        self.assertIn(str(cr.pk), cr.get_absolute_url())

    def test_candidate_ranking_non_unique_rank(self):
        """Test that creating a CandidateRanking with a non unique rank
        fails"""

        rank = 16

        self.job.save()
        self.cl.save()
        error_msg = "{'__all__': ['Candidate ranking with this Candidate " +\
            "list and Rank already exists.']}"

        cr = CandidateRanking(candidate_list=self.cl,
                              candidate=self.auth_user,
                              rank=rank)
        cr.full_clean()
        cr.save()

        cr_2 = CandidateRanking(candidate_list=self.cl,
                                candidate=self.basic_user,
                                rank=rank)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 cr_2.full_clean)
        self.assertEqual(CandidateRanking.objects.all().count(), 1)
        self.assertEqual(self.cl.rankings.count(), 1)
        self.assertEqual(self.auth_user.rankings.count(), 1)

    def test_candidate_ranking_non_unique_candidate(self):
        """Test that creating a CandidateRanking with a non unique candidate
        fails"""

        rank = 16
        rank_2 = 32

        self.job.save()
        self.cl.save()
        error_msg = "{'__all__': ['Candidate ranking with this Candidate " +\
            "list and Candidate already exists.']}"

        cr = CandidateRanking(candidate_list=self.cl,
                              candidate=self.auth_user,
                              rank=rank)
        cr.full_clean()
        cr.save()

        cr_2 = CandidateRanking(candidate_list=self.cl,
                                candidate=self.auth_user,
                                rank=rank_2)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 cr_2.full_clean)
        self.assertEqual(CandidateRanking.objects.all().count(), 1)
        self.assertEqual(self.cl.rankings.count(), 1)
        self.assertEqual(self.auth_user.rankings.count(), 1)

    def test_candidate_ranking_bad_rank(self):
        """Test that creating a CandidateRanking with a bad rank
        fails"""

        rank = -1

        self.job.save()
        self.cl.save()
        error_msg = "{'rank': ['Ensure this value is greater than or equal" +\
            ERROR_MSG_VALUE

        cr = CandidateRanking(candidate_list=self.cl,
                              candidate=self.auth_user,
                              rank=rank)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 cr.full_clean)
        self.assertEqual(CandidateRanking.objects.all().count(), 0)
        self.assertEqual(self.cl.rankings.count(), 0)
        self.assertEqual(self.auth_user.rankings.count(), 0)

    def test_learning_plan(self):
        """Test that creating a Learning Plan is successful"""

        name = "Test Learning Plan"
        timeframe = "Short-term (1-2 years)"

        lp = LearningPlan(name=name,
                          timeframe=timeframe,
                          learner=self.auth_user)
        lp.full_clean()
        lp.save()

        self.assertEqual(lp.name, name)
        self.assertEqual(lp.timeframe, timeframe)
        self.assertEqual(lp.learner, self.auth_user)
        self.assertIn(name, str(lp))
        self.assertIn(str(self.auth_user), str(lp))
        self.assertIn(timeframe, str(lp))
        self.assertEqual(LearningPlan.objects.all().count(), 1)
        self.assertEqual(self.auth_user.learning_plans.count(), 1)
        self.assertIn(str(lp.pk), lp.get_absolute_url())

    def test_learning_plan_competency(self):
        """Test that creating a Learning Plan Competency is successful"""

        priority = "High"
        self.learning_plan.save()
        self.competency.save()

        lpc = LearningPlanCompetency(learning_plan=self.learning_plan,
                                     eccr_competency=self.competency,
                                     priority=priority)
        lpc.full_clean()
        lpc.save()

        self.assertEqual(lpc.learning_plan, self.learning_plan)
        self.assertEqual(lpc.eccr_competency, self.competency)
        self.assertEqual(lpc.priority, priority)
        self.assertIn(str(self.learning_plan), str(lpc))
        self.assertIn(str(self.competency), str(lpc))
        self.assertIn(priority, str(lpc))
        self.assertEqual(LearningPlanCompetency.objects.all().count(), 1)
        self.assertEqual(self.learning_plan.competencies.count(), 1)
        self.assertEqual(self.competency.
                         learning_plans_competencies.count(), 1)
        self.assertIn(str(lpc.pk), lpc.get_absolute_url())

    def test_learning_plan_goal(self):
        """Test that creating a Learning Plan Goal is successful"""

        goal_name = "Test Goal"
        timeline = 6
        resources_support = ["test_resource1", "test_resource2"]
        obstacles = ["test_obstacle1", "test_obstacle2"]
        resources_support_other = "Other test resource"
        obstacles_other = "Other test obstacle"

        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()

        lpg = LearningPlanGoal(plan_competency=self.learning_plan_competency,
                               goal_name=goal_name,
                               timeline=timeline,
                               resources_support=resources_support,
                               obstacles=obstacles,
                               resources_support_other=resources_support_other,
                               obstacles_other=obstacles_other)
        lpg.full_clean()
        lpg.save()

        self.assertEqual(lpg.plan_competency, self.learning_plan_competency)
        self.assertEqual(lpg.goal_name, goal_name)
        self.assertEqual(lpg.timeline, timeline)
        self.assertEqual(lpg.resources_support, resources_support)
        self.assertEqual(lpg.obstacles, obstacles)
        self.assertEqual(lpg.resources_support_other, resources_support_other)
        self.assertEqual(lpg.obstacles_other, obstacles_other)
        self.assertIn(str(self.learning_plan_competency), str(lpg))
        self.assertIn(goal_name, str(lpg))
        self.assertEqual(LearningPlanGoal.objects.all().count(), 1)
        self.assertEqual(self.learning_plan_competency.goals.count(), 1)
        self.assertIn(str(lpg.pk), lpg.get_absolute_url())

    def test_learning_plan_goal_ksa(self):
        """Test that creating a Learning Plan Goal KSA is successful"""

        current_proficiency = "test_low"
        target_proficiency = "test_medium"

        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        self.learning_plan_goal.save()
        self.ksa.save()

        lpgk = LearningPlanGoalKsa(plan_goal=self.learning_plan_goal,
                                   eccr_ksa=self.ksa,
                                   current_proficiency=current_proficiency,
                                   target_proficiency=target_proficiency)
        lpgk.full_clean()
        lpgk.save()

        self.assertEqual(lpgk.plan_goal, self.learning_plan_goal)
        self.assertEqual(lpgk.eccr_ksa, self.ksa)
        self.assertEqual(lpgk.current_proficiency, current_proficiency)
        self.assertEqual(lpgk.target_proficiency, target_proficiency)
        self.assertIn(str(self.learning_plan_goal), str(lpgk))
        self.assertIn(str(self.ksa), str(lpgk))
        self.assertIn(current_proficiency, str(lpgk))
        self.assertIn(target_proficiency, str(lpgk))
        self.assertEqual(LearningPlanGoalKsa.objects.all().count(), 1)
        self.assertEqual(self.learning_plan_goal.ksas.count(), 1)
        self.assertEqual(self.ksa.learning_plans_ksas.count(), 1)
        self.assertIn(str(lpgk.pk), lpgk.get_absolute_url())

    def test_learning_plan_goal_course(self):
        """Test that creating a Learning Plan Goal Course is successful"""

        self.learning_plan.save()
        self.competency.save()
        self.learning_plan_competency.save()
        self.learning_plan_goal.save()
        self.course.save()

        lpgc = LearningPlanGoalCourse(plan_goal=self.learning_plan_goal,
                                      xds_course=self.course)
        lpgc.full_clean()
        lpgc.save()

        self.assertEqual(lpgc.plan_goal, self.learning_plan_goal)
        self.assertEqual(lpgc.xds_course, self.course)
        self.assertIn(str(self.learning_plan_goal), str(lpgc))
        self.assertIn(str(self.course), str(lpgc))
        self.assertEqual(LearningPlanGoalCourse.objects.all().count(), 1)
        self.assertEqual(self.learning_plan_goal.courses.count(), 1)
        self.assertEqual(self.course.xds_courses.count(), 1)
        self.assertIn(str(lpgc.pk), lpgc.get_absolute_url())

    def test_application(self):
        """Test that creating an Application is successful"""

        app = Application.objects.create(
            applicant=self.auth_user,
            code_of_ethics_acknowledgement=True,
            application_type=Application.ApplicationChoices.NEW,
            position=Application.PositionChoices.SAPR_VA,
            status=Application.StatusChoices.DRAFT,
            policy='test-policy',
            application_version=2,
            first_name='John',
            last_name='Smith',
            middle_initial='Q',
            affiliation='Army',
            mili_status='Active',
            rank='Captain',
            grade='O-3',
            command_unit='Unit A',
            installation='Base X',
            work_email='john.smith@army.mil',
            has_mil_gov_work_email=True,
            other_sarc_email='other.sarc@army.mil',
            dsn_code='12345',
            work_phone='555-0101',
            work_phone_ext='123',
            certification_awarded_date=date(2023, 1, 1),
            certification_expiration_date=date(2025, 1, 1),
            no_experience_needed=True,
            supervisor_first_name='Sue',
            supervisor_last_name='Officer',
            supervisor_email='sue.officer@army.mil',
            sarc_first_name='Mary',
            sarc_last_name='Sarc',
            sarc_email='mary.sarc@army.mil',
            commanding_officer_first_name='Carl',
            commanding_officer_last_name='Commander',
            commanding_officer_email='carl.commander@army.mil',
            co_same_as_supervisor=True,
            final_submission=True,
            final_submission_stamp=datetime(2025, 1, 2, 10, 30),
        )
        # Check field values
        self.assertEqual(app.applicant, self.auth_user)
        self.assertTrue(app.code_of_ethics_acknowledgement)
        self.assertEqual(app.application_type,
                         Application.ApplicationChoices.NEW)
        self.assertEqual(app.position, Application.PositionChoices.SAPR_VA)
        self.assertEqual(app.status, Application.StatusChoices.DRAFT)
        self.assertEqual(app.policy, 'test-policy')
        self.assertEqual(app.application_version, 2)
        self.assertEqual(app.first_name, 'John')
        self.assertEqual(app.last_name, 'Smith')

        # Test the __str__ method
        self.assertEqual(
            str(app),
            f'{Application.ApplicationChoices.NEW} - John Smith '
            f'({Application.StatusChoices.DRAFT})'
        )

    def test_application_experience(self):
        """Test that creating an ApplicationExperience is successful"""

        app_exp = ApplicationExperience.objects.create(
            application=self.application,
            display_order=1,
            position_name='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            advocacy_hours=2000,
            marked_for_evaluation=True,
            supervisor_last_name="Super",
            supervisor_first_name="Steven",
            supervisor_email="steven.super@example.com",
            supervisor_not_available=False,
        )

        # Check field values
        self.assertEqual(app_exp.application, self.application)
        self.assertEqual(app_exp.position_name, 'Software Engineer')
        self.assertEqual(app_exp.start_date, date(2020, 1, 1))
        self.assertEqual(app_exp.end_date, date(2022, 12, 31))
        self.assertEqual(app_exp.advocacy_hours, 2000)
        self.assertTrue(app_exp.marked_for_evaluation)
        self.assertEqual(app_exp.supervisor_last_name, "Super")
        self.assertEqual(app_exp.supervisor_first_name, "Steven")
        self.assertEqual(app_exp.supervisor_email, "steven.super@example.com")
        self.assertFalse(app_exp.supervisor_not_available)

        # Test the __str__ method
        self.assertEqual(
            str(app_exp),
            'Software Engineer for Application ' + str(self.application.id)
        )

    def test_application_course(self):
        """Test that creating an ApplicationCourse is successful"""

        self.course.save()

        app_course = ApplicationCourse.objects.create(
            application=self.application,
            display_order=1,
            category='Cybersecurity',
            xds_course=self.course,
            completion_date=date(2021, 6, 15),
            clocked_hours=40,
        )

        # Check field values
        self.assertEqual(app_course.application, self.application)
        self.assertEqual(app_course.display_order, 1)
        self.assertEqual(app_course.category, 'Cybersecurity')
        self.assertEqual(app_course.xds_course, self.course)
        self.assertEqual(app_course.completion_date, date(2021, 6, 15))
        self.assertEqual(app_course.clocked_hours, 40)

        # Test the __str__ method
        self.assertEqual(
            str(app_course),
            'Course abcdefg12345 for Application ' + str(self.application.id)
        )

    def test_application_comment(self):
        """Test that creating an ApplicationComment is successful"""

        comment_text = "This is a test comment."

        app_comment = ApplicationComment.objects.create(
            application=self.application,
            reviewer=self.auth_user,
            comment=comment_text,
        )

        # Check field values
        self.assertEqual(app_comment.application, self.application)
        self.assertEqual(app_comment.reviewer, self.auth_user)
        self.assertEqual(app_comment.comment, comment_text)

        # Test the __str__ method
        self.assertEqual(
            str(app_comment),
            f'Comment by {self.auth_user.username} on '
            f'Application ' + f'{self.application.id}'
        )
