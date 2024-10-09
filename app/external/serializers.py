import logging

from rest_framework import serializers

from external.models import Course, Job, LearnerRecord

logger = logging.getLogger(__name__)


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['name',
                  'reference',]


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['name',
                  'job_type',
                  'reference',]


class LearnerRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearnerRecord
        fields = ['name',
                  'user',]
