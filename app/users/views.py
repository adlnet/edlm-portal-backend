from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer


class IsLoggedInView(APIView):
    """Checks if a user is logged in"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return the user details if logged in
        (permission_classes checks authentication)
        """
        return Response({"user": UserSerializer(request.user).data},
                        status=status.HTTP_200_OK)
