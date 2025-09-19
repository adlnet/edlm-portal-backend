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
        Validates that a user has a valid sessionid
        """
        # if the user is not found/authenticated (invalid session id)
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response({"user": UserSerializer(request.user).data},
                        status=status.HTTP_200_OK)
