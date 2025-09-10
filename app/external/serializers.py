import logging

from rest_framework import serializers

from configuration.utils.portal_utils import confusable_homoglyphs_check
from external.models import Course, Job, LearnerRecord

logger = logging.getLogger(__name__)
HOMOGLYPH_ERROR = "Data contains homoglyphs and can be dangerous. Check" + \
    " logs for more details"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['name',
                  'reference',]

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['name',
                  'job_type',
                  'reference',]
        extra_kwargs = {
            'reference': {'validators': []},
        }

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class LearnerRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearnerRecord
        fields = ['name',
                  'user',]

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)
