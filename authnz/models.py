from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext

from authnz.tasks import send_email
from authnz.utils import email_activation_token
from authnz.permissions import check_permission_previous_send_email_count
from utils.exceptions import FeedCloudBaseException


class User(AbstractUser):
    email_confirmed = models.BooleanField(
        default=False, help_text=gettext("Email verified.")
    )

    class Meta:
        indexes = (
            models.Index(fields=("email",)),
        )

    def __str__(self):
        return self.username

    def confirm_email(self):
        """
        Confirms user email
        :return:
        """
        self.email_confirmed = True
        self.save()

    @classmethod
    def register_user(cls, email: str, password: str) -> User:
        """
        Handles user registration request
        :param email:
        :param password:
        :return:
        """
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist as e:
            user = None

        if user and user.email_confirmed:
            raise FeedCloudBaseException(detail=gettext("You registered before."))

        if user:  # registered before but not confirmed, so just renew password
            user.update_password(password)
        else:
            user = User.create_user(email, password)  # create user
        return user

    def update_password(self, raw_password):
        """
        Updates user password
        :param raw_password:
        :return:
        """
        self.set_password(raw_password)
        self.save()

    @classmethod
    def create_user(cls, email, password):
        """
        Creates a user
        :param email:
        :param password:
        :return:
        """
        user = cls(username=email, email=email)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def login_user(cls, email: str, password: str, request) -> User:
        """
        Handles user request for login

            if it succeed it will return an instance of user

            if it failed it will raise a proper exception

        :param email:
        :param password:
        :param request:
        :return:
        """
        try:
            user = User.objects.get(email=email)
        except cls.DoesNotExist as e:
            raise FeedCloudBaseException(
                detail=gettext("You did not registered before.")
            )
        if user.email_confirmed and user.is_active and user.check_password(password):
            return user
        elif not user.email_confirmed:
            # in case user didn't approved his/her email. send email again
            check_permission_previous_send_email_count(email)
            user.send_email_confirm(request)
            # we sent an email to user but we should respond with an error
            raise FeedCloudBaseException(
                detail=gettext(
                    "You did not confirm your email,"
                    " We sent you a confirmation email"
                )
            )
        elif not user.is_active:
            raise FeedCloudBaseException(
                detail=gettext("Your account is not active, please contact support.")
            )
        else:
            raise FeedCloudBaseException(detail=gettext("Wrong login credentials."))

    def send_email_confirm(self, request):
        """
        Sends email verification
        :param request:
        :return:
        """
        current_site = get_current_site(request)
        template_context = {
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(self.pk)),
            "token": email_activation_token.make_token(self),
            "http_type": "https" if request.is_secure() else "http",
        }
        send_email.apply_async((self.email, template_context))

    def check_email_activation_token(self, token: str) -> bool:
        """
        Checks token used in user email for verification
        :param token:
        :return:
        """
        return email_activation_token.check_token(self, token)
