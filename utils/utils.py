from django.utils.translation import gettext

from utils.exceptions import FeedCloudBaseException


def pagination_util(request) -> (int, int):
    arguments = request.query_params
    try:
        size = int(arguments.get("size", 20))
        index = int(arguments.get("index", 0))
    except ValueError:
        raise FeedCloudBaseException(
            detail=gettext("Size and index query param for pagination must be integer.")
        )
    size = index + size
    return index, size
