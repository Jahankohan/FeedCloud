from django.db.utils import IntegrityError
from django.utils.translation import gettext
from rest_framework import generics, status

from utils.exceptions import FeedCloudBaseException
from utils.responses import SuccessResponse


class CreateView(generics.CreateAPIView):
    """
    Create instance
    """

    def post(self, request, *args, **kwargs):
        serialize_data = self.get_serializer(data=request.data)
        serialize_data.is_valid(raise_exception=True)
        try:
            self.perform_create(serialize_data)
        except IntegrityError as e:
            raise FeedCloudBaseException(
                detail=gettext("Duplicate instance."), code=status.HTTP_409_CONFLICT
            )
        return SuccessResponse(serialize_data.data, status=status.HTTP_201_CREATED)
