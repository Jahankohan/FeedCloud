from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext
from rest_framework import decorators, generics, views, status
from rest_framework.permissions import IsAuthenticated

from authnz import serializers as authnz_serializers
from authnz.models import User
from authnz.permissions import check_permission_previous_send_email_count
from authnz.utils import jwt_response_payload_handler
from utils import (
    exceptions as custom_exceptions,
    responses,
)
from utils.tools import retrieve, update


@decorators.authentication_classes(())
@decorators.permission_classes(())
class UserRegisterEmailView(generics.CreateAPIView):
    """
    post:

        Register

            Register new user with email and password

            if user registered before but he didn't approved his email, this view
            will update user password with new password and raise exception

            email min 5, max 50

            password min 8, max 50,
            should have number,
            shouldn't be common or similar to user attrs

    """

    serializer_class = authnz_serializers.RegisterEmailSerializer
    throttle_rate = "10/day"

    def post(self, request, *args, **kwargs):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        check_permission_previous_send_email_count(serialized_data.data["email"])
        user = User.register_user(
            serialized_data.data["email"], serialized_data.data["password"]
        )
        user.send_email_confirm(request)
        return responses.SuccessResponse(
            {}, message=gettext("Check your email."), status=status.HTTP_201_CREATED
        )


@decorators.authentication_classes(())
@decorators.permission_classes(())
class UserLoginEmailView(generics.CreateAPIView):
    """
    post:

        Login

            Login with email & password

            email min 5, max 50

            password min 8, max 50

    """

    serializer_class = authnz_serializers.LoginEmailSerializer
    throttle_rate = "10/hour"

    def post(self, request, *args, **kwargs):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        email = serialized_data.data["email"]
        password = serialized_data.data["password"]
        user = User.login_user(email, password, request)
        jwt_token = jwt_response_payload_handler(user)
        return responses.SuccessResponse(jwt_token)


@decorators.permission_classes((IsAuthenticated,))
class UserRefreshTokenView(views.APIView):
    """
    get:

        Refresh JWT token

            Refresh JWT token

            token is valid for just 10 days, client should renew token before expiration,
            unless user should login again
    """

    throttle_classes = ()

    def get(self, request, *args, **kwargs):
        if request.user.is_active:
            jwt_token = jwt_response_payload_handler(request.user)
            return responses.SuccessResponse(jwt_token)
        else:
            raise custom_exceptions.FeedCloudBaseException(
                detail=gettext("This user is inactive, contact us.")
            )


@decorators.authentication_classes(())
@decorators.permission_classes(())
class UserConfirmEmailView(views.APIView):
    """
    get:

        Confirm email

            Confirm email with a link in confirm email sent to user
    """

    throttle_classes = ()

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and user.check_email_activation_token(token):
            user.confirm_email()
            return render(request, "authnz/mail_confirmed.html")
        else:
            return render(
                request,
                "authnz/mail_confirm_invalid.html",
                status=status.HTTP_400_BAD_REQUEST,
            )


@decorators.permission_classes((IsAuthenticated,))
class UserMyProfileView(retrieve.RetrieveView, update.UpdateView):
    """
    get:

        my profile

            Get my user profile info

            email   str

            email_confirmed     bool

            first_name  str

            last_name   str

    put:

        update profile

            update user profile

            first_name str min 5, max 50 allow blank for remove optional

            last_name str min 5, max 50  allow blank for remove optional


    patch:

        update profile

            update user profile

            first_name str min 5, max 50 allow blank for remove optional

            last_name str min 5, max 50  allow blank for remove optional

    """

    serializer_class = authnz_serializers.MyProfileSerializer
    model = User
    throttle_classes = ()
