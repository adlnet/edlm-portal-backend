import json
from unittest.mock import mock_open, patch

from django.core.exceptions import ValidationError
from django.test import tag

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse)

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_profile_question(self):
        """Test that creating a ProfileQuestion is successful"""

        active = True
        order = 32
        question = "What color is the sky?"

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

    def test_profile_question_bad_order(self):
        """Test that creating a ProfileQuestion with a wrong order fails"""

        active = True
        order = -32
        question = "What color is the sky?"
        error_msg = "{'order': ['Ensure this value is greater than or equal" +\
            " to 0.']}"

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
        question = "What color is the sky?"
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
        question = "What color is the sky?"
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
            " to 0.']}"

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
            " to 0.']}"

        cr = CandidateRanking(candidate_list=self.cl,
                              candidate=self.auth_user,
                              rank=rank)

        self.assertRaisesMessage(ValidationError, error_msg,
                                 cr.full_clean)
        self.assertEqual(CandidateRanking.objects.all().count(), 0)
        self.assertEqual(self.cl.rankings.count(), 0)
        self.assertEqual(self.auth_user.rankings.count(), 0)
