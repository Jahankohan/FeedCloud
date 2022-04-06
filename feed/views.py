from django.db.utils import IntegrityError
from django.utils.translation import gettext
from rest_framework import (
    decorators,
    generics,
    status,
    views,
)
from rest_framework.permissions import IsAuthenticated

from feed.models import Feed, Entry
from feed.serializers import (
    FeedSerializers,
    EntrySerializers,
    NestedFeedEntrySerializer,
)
from utils import exceptions, responses, utils
from utils.tools import create, update


# Feed
@decorators.permission_classes((IsAuthenticated,))
class FeedCreateListView(create.CreateView):
    """
    post:

        Create Rss

            title min 3, max 100 optional

            link min 5, max 200

            timeout 1-10 default 2

            example

                title   zoomit

                link    https://www.zoomit.ir/feed/
    get:

        Get list of available feeds

            pagination with index and size

            /?index=0&size=20

            filter

                title

                for staffs

                    status  P for pending, A for active, e for error and blank  for all
    """

    serializer_class = FeedSerializers
    model = Feed
    throttle_rate = "200/hour"

    def get(self, request, *args, **kwargs):
        index, size = utils.pagination_util(request)
        args = request.query_params
        filters = {}
        if args.get("title"):
            filters["title__icontains"] = args["title"]

        if args.get("status") and request.user.is_staff:
            filters["status"] = args["status"]
        elif not request.user.is_staff:
            filters["status"] = Feed.ACTIVE

        feed_query = self.model.objects.filter(**filters)
        total = feed_query.count()

        data = self.get_serializer(feed_query[index:size], many=True).data
        return responses.SuccessResponse(data, index=index, total=total)


@decorators.permission_classes((IsAuthenticated,))
class FeedCreatedByMeListView(generics.GenericAPIView):
    """
    get:

        Get list of feeds created by user

            pagination with index and size

            /?index=0&size=20

            filter

                title
    """

    serializer_class = FeedSerializers
    model = Feed
    throttle_classes = ()

    def get(self, request, *args, **kwargs):
        index, size = utils.pagination_util(request)
        args = request.query_params
        filters = {
            "creator": request.user,
        }
        if args.get("title"):
            filters["title__icontains"] = args["title"]

        feed_query = self.model.objects.filter(**filters)
        total = feed_query.count()

        data = self.get_serializer(
            feed_query[index:size],
            context={"request": request, "my_feeds": True},
            many=True,
        ).data
        return responses.SuccessResponse(data, index=index, total=total)


@decorators.permission_classes([IsAuthenticated])
class FeedUpdateView(update.UpdateView):
    """
    put:

        Update Feed

            Update Feed by staff or creator of feed

                title min 3, max 100 optional

                link min 5, max 200

                force_update bool

    patch:

        Update Feed

            Update Feed by staff or creator of feed

                title min 3, max 100

                link min 5, max 200

                bool


    """

    serializer_class = FeedSerializers
    model = Feed
    throttle_rate = "20/day"


@decorators.permission_classes([IsAuthenticated])
class FeedFollowView(generics.GenericAPIView):
    """
    get:

        List of followed feeds

            Get my list of followed feeds

                pagination with index and size

                /?index=0&size=20

                filter

                    title

                        search on feed title

    post:

        Follow feed

            Follow feed by id

    """

    serializer_class = NestedFeedEntrySerializer
    model = Feed
    throttle_classes = ()

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        feed_id = serialized_data.data["id"]
        try:
            request.user.feed_followed.add(feed_id)
        except IntegrityError as e:
            if 'is not present in table "feed_feed"' in "".join(e.args):
                raise exceptions.FeedCloudBaseException(
                    gettext(f"Feed {feed_id} does not exist."),
                    code=status.HTTP_404_NOT_FOUND,
                )
        return responses.SuccessResponse({})

    def get(self, request, *args, **kwargs):
        index, size = utils.pagination_util(request)
        args = request.query_params
        filters = {
            "followers": request.user,
        }
        if args.get("title"):
            filters["title__icontains"] = args["title"]
        feed_query = self.model.objects.filter(**filters)
        total = feed_query.count()
        data = FeedSerializers(
            feed_query[index:size], context={"request": request}, many=True
        ).data
        return responses.SuccessResponse(data, index=index, total=total)


@decorators.permission_classes([IsAuthenticated])
class FeedUnFollowView(views.APIView):
    """
    delete:

        Unfollow feed

            Unfollow feed by id

    """

    throttle_classes = ()

    def delete(self, request, feed_id, *args, **kwargs):
        request.user.feed_followed.remove(feed_id)
        return responses.SuccessResponse(status=status.HTTP_204_NO_CONTENT)


# Entry
@decorators.permission_classes([IsAuthenticated])
class EntryListView(generics.GenericAPIView):
    """
    get:

        Entry list

            Get list of available entries

                pagination with index and size

                /?index=0&size=20

                filter

                    title

                        for search on entry titles

                    read

                        true for read

                        false for unread

                        blank for all

                order_by

                    OLDEST

                    NEWEST default

    """

    serializer_class = EntrySerializers
    model = Entry
    throttle_classes = ()

    def get(self, request, feed_id: int = None, *args, **kwargs):
        index, size = utils.pagination_util(request)
        args = request.query_params
        filters = {}
        if feed_id:
            if not Feed.objects.filter(id=feed_id).exists():
                raise exceptions.FeedCloudBaseException(
                    gettext(f"Feed {feed_id} does not exist."),
                    code=status.HTTP_404_NOT_FOUND,
                )

            filters["feed"] = feed_id

        if args.get("title"):
            filters["title__icontains"] = args["title"]

        entry_query = self.model.objects.filter(**filters)

        if args.get("read"):
            if args["read"].lower() == "true":
                entry_query = entry_query.exclude(reads=None)
            elif args["read"].lower() == "false":
                entry_query = entry_query.filter(reads=None)
            else:
                raise exceptions.FeedCloudBaseException(
                    gettext("read query param value should be true, false or blank.")
                )

        if args.get("order_by") and args["order_by"] == "OLDEST":
            entry_query = entry_query.order_by("published")

        total = entry_query.count()
        data = self.get_serializer(entry_query[index:size], many=True).data
        return responses.SuccessResponse(data, index=index, total=total)


@decorators.permission_classes([IsAuthenticated])
class EntryReadView(generics.GenericAPIView):
    """
    post:

        Read entry

            Read entry by id

    """

    serializer_class = NestedFeedEntrySerializer
    throttle_classes = ()

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        entry_id = serialized_data.data["id"]
        try:
            request.user.entries_read.add(entry_id)
        except IntegrityError as e:
            if 'is not present in table "feed_entry"' in "".join(e.args):
                raise exceptions.FeedCloudBaseException(
                    gettext(f"Entry {entry_id} does not exist."),
                    code=status.HTTP_404_NOT_FOUND,
                )
        return responses.SuccessResponse({})
