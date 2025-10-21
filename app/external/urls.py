from django.urls import include, path
from rest_framework.routers import DefaultRouter

from external import views

app_name = 'ext'

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet,
                basename='courses')
router.register(r'jobs', views.JobViewSet,
                basename='jobs')
router.register('learners', views.LearnerRecordViewSet,
                basename='learners')
router.register(r'competencies', views.CompetencyViewSet,
                basename='competencies')
router.register(r'ksas', views.KsaViewSet,
                basename='ksas')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
