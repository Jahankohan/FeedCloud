import logging

from django.utils.translation import gettext
from rest_framework import exceptions, status

from utils.responses import ErrorResponse


logger = logging.getLogger(__name__)


class FeedCloudBaseException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext("Operation failed.")

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        if detail:
            self.detail = detail
        if code:
            self.status_code = code

    def __repr__(self):
        return f"FeedCloudBaseException({self.detail}, {self.status_code})"

    def __str__(self):
        return (
            f"FeedCloudBaseException detail: {self.detail}, status {self.status_code}"
        )


def custom_exception_handler(exception, data):
    if isinstance(exception, exceptions.APIException):
        logger.error(
            f"{exception.detail} in url {data['view'].request.get_full_path()}"
        )
        return ErrorResponse(message=exception.detail, status=exception.status_code)
