from django.urls import include, path
from rest_framework.routers import DefaultRouter

from configuration import views

app_name = 'config'

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'config', views.ConfigurationViewSet,
                basename='config')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
