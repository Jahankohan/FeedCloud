from datetime import datetime

import pytz
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext

from utils.responses import ErrorResponse


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            st = datetime.now().astimezone()
            response = self.get_response(request)
            print("Response Ready in: ", datetime.now().astimezone() - st)
        else:
            response = self.get_response(request)
        return response


class TimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            timezone.activate(
                pytz.timezone(request.headers.get("Timezone", settings.TIME_ZONE))
            )
        except pytz.exceptions.UnknownTimeZoneError as e:
            return ErrorResponse(message=gettext(f"Unknown timezone: {e}"))
        response = self.get_response(request)
        return response
