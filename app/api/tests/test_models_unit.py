import json
from unittest.mock import mock_open, patch

from django.core.exceptions import ValidationError
from django.test import tag

from api.models import ProfileAnswer, ProfileQuestion, ProfileResponse

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
