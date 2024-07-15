from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'profile-questions', views.ProfileQuestionViewSet,
                basename='profile-questions')
router.register(r'profile-responses', views.ProfileResponseViewSet,
                basename='profile-responses')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
