from rest_framework.throttling import SimpleRateThrottle


WHITE_LIST_VIEWS = [
    "SchemaView",
    "UserConfirmEmailView",
]


class CustomViewRateThrottle(SimpleRateThrottle):
    scope = "user_view"

    def __init__(self):
        pass

    def get_cache_key(self, request, view):
        """
        Get cache key based on user username or ip of request
        :param request:
        :param view:
        :return:
        """
        if request.user.is_authenticated:
            ident = request.user.username
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": "_".join([view.__class__.__name__, str(ident)]),
        }

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.

        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if view.__class__.__name__ in WHITE_LIST_VIEWS:
            return True

        self.rate = self.get_rate(request)
        if self.rate is None:
            return True
        self.num_requests, self.duration = self.parse_rate(self.rate)

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def get_rate(self, request):
        """
        Determine the string representation of the allowed request rate.
        """
        if hasattr(request.parser_context["view"], "throttle_rate"):
            return request.parser_context["view"].throttle_rate
        else:
            if request.user.is_authenticated:
                if request.user.is_staff:
                    return None
                else:
                    return "100/hour"
            else:
                return "1000/day"
