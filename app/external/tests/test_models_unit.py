from django.test import tag

from external.models import Course, Job, LearnerRecord

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_course(self):
        """Test that creating a Course is successful"""
        name = "course_name"
        reference = "course_ref"

        course = Course(name=name,
                        reference=reference)
        course.full_clean()
        course.save()

        self.assertEqual(course.name, name)
        self.assertEqual(course.reference, reference)
        self.assertEqual(str(course), name)
        self.assertEqual(Course.objects.all().count(), 1)

    def test_multiple_course(self):
        """Test that creating 2 Courses fails"""
        name = "course_name"
        name2 = "other name"
        reference = "course_ref"

        course = Course(name=name,
                        reference=reference)
        course.full_clean()
        course.save()

        course2 = Course(name=name2,
                         reference=reference)
        course2.save()

        self.assertEqual(course.name, name)
        self.assertEqual(course.reference, reference)
        self.assertEqual(Course.objects.all().count(), 1)

    def test_job(self):
        """Test that creating a Job is successful"""
        name = "job_name"
        reference = "job_ref"
        job_type = "job_type"

        job = Job(name=name, job_type=job_type,
                  reference=reference)
        job.full_clean()
        job.save()

        self.assertEqual(job.name, name)
        self.assertEqual(job.reference, reference)
        self.assertEqual(job.job_type, job_type)
        self.assertEqual(str(job), name)
        self.assertEqual(Job.objects.all().count(), 1)

    def test_multiple_job(self):
        """Test that creating 2 Jobs fails"""
        name = "job_name"
        name = "other name"
        reference = "job_ref"
        job_type = "job_type"
        job_type = "other type"

        job = Job(name=name, job_type=job_type,
                  reference=reference)
        job.full_clean()
        job.save()

        job2 = Job(name=name, job_type=job_type,
                   reference=reference)
        job2.save()

        self.assertEqual(job.name, name)
        self.assertEqual(job.reference, reference)
        self.assertEqual(job.job_type, job_type)
        self.assertEqual(Job.objects.all().count(), 1)

    def test_learner_record(self):
        """Test that creating a LearnerRecord is successful"""
        name = "record_name"

        lr = LearnerRecord(name=name,
                           user=self.basic_user)
        lr.full_clean()
        lr.save()

        self.assertEqual(lr.name, name)
        self.assertEqual(lr.user, self.basic_user)
        self.assertEqual(str(lr), name)
        self.assertEqual(LearnerRecord.objects.all().count(), 1)
