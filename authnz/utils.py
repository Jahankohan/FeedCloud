from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework_simplejwt.tokens import RefreshToken


class EmailActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Email verification code
    """

    def _make_hash_value(self, user, timestamp: int) -> str:
        return f"{user.pk}{timestamp}{user.email_confirmed}"


email_activation_token = EmailActivationTokenGenerator()


def generate_token(user):
    """
    Generates JWT token for user
    :param user:
    :return:
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


def jwt_response_payload_handler(user):
    """
    Returns the response data for both the login and refresh token views.
    :param user:
    """
    from authnz.serializers import MyProfileSerializer

    data = {
        "token": generate_token(user),
        "user": MyProfileSerializer(user).data,
    }
    return data
