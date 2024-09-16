from django.urls import include, path
from graph import views
from rest_framework.routers import DefaultRouter

# Create a router and register our ViewSets with it.
router = DefaultRouter()
# router.register(r'graph', views.GraphView.as_view(),
#                 basename='graph')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('graph/', views.GraphView.as_view()),
]
