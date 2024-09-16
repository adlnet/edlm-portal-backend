from knox.auth import TokenAuthentication
from knox.views import LoginView


class GenerateAPIKeyFromOtherAuthMethod(LoginView):
    """
    This API is for generating API Keys using Django-Rest-Knox without
    allowing an API Key to be used to generate a new API Key
    """

    def get_authenticators(self):
        """Overrides method to remove Token Authentication from available
        authentication methods"""
        return [auth for auth in super().get_authenticators() if not
                isinstance(auth, TokenAuthentication)]
