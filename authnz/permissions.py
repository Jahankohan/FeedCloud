from django.utils.translation import gettext
from django.core.cache import cache
from django.conf import settings
from rest_framework import status

from utils.exceptions import FeedCloudBaseException


def check_permission_previous_send_email_count(email: str, silence=False) -> bool:
    """
    Checks count of previous emails sent for user
    :param email:
    :param silence:
    :return:
    """
    email_count = cache.get(f"{settings.EMAIL_SEND_COUNT}_{email}", 0)
    if email_count >= settings.MAX_EMAIL_SEND_COUNT:
        if silence:
            return False
        raise FeedCloudBaseException(
            detail=gettext("Max email send reached, try later."),
            code=status.HTTP_403_FORBIDDEN,
        )
    return True


def increase_send_email_count(email):
    """
    Adds to user sent email count
    :param email:
    :return:
    """
    email_count = cache.get(f"{settings.EMAIL_SEND_COUNT}_{email}", 0)
    cache.set(
        "{}_{}".format(settings.EMAIL_SEND_COUNT, email),
        email_count + 1,
        timeout=settings.MAX_EMAIL_SEND_TIMEOUT,
    )
