from django.utils.translation import gettext
from rest_framework import generics, status

from authnz.models import User
from utils.exceptions import FeedCloudBaseException
from utils.responses import SuccessResponse


class RetrieveView(generics.RetrieveAPIView):
    """
    Retrieve instance
    """

    def get(self, request, instance_id: int = None, *args, **kwargs):
        if instance_id:
            instance = self.model.objects.get(id=instance_id)
        elif self.model == User:
            instance = request.user
        else:
            raise FeedCloudBaseException(
                detail=gettext("Not implemented"),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        serialize_data = self.get_serializer(instance)
        return SuccessResponse(serialize_data.data)
