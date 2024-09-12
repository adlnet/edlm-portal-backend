from django.urls import include, path
from rest_framework.routers import DefaultRouter

from external import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet,
                basename='courses')
router.register(r'jobs', views.JobViewSet,
                basename='jobs')
router.register('learners', views.LearnerRecordViewSet,
                basename='learners')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
