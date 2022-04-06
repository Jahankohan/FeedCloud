from django.utils.translation import gettext
from rest_framework import generics, status

from authnz.models import User
from utils.exceptions import FeedCloudBaseException
from utils.responses import SuccessResponse
from utils.permissions import check_update_permission


class UpdateView(generics.UpdateAPIView):
    """
    Update instance
    """

    def put(self, request, instance_id: int = None, *args, **kwargs):
        instance = self._get_instance(request, instance_id)
        serialized_data = self.get_serializer(instance, data=request.data)
        serialized_data.is_valid(raise_exception=True)
        self.perform_update(serialized_data)
        return SuccessResponse(serialized_data.data)

    def patch(
        self, request, instance_id: int = None, *args, **kwargs
    ):  # just send parameters you want to update, don't need all of them
        instance = self._get_instance(request, instance_id)
        serialized_data = self.get_serializer(instance, data=request.data, partial=True)
        serialized_data.is_valid(raise_exception=True)
        self.perform_update(serialized_data)
        return SuccessResponse(serialized_data.data)

    def _get_instance(self, request, instance_id: int = None):
        if instance_id:
            instance = self.model.objects.get(id=instance_id)
            check_update_permission(request, instance)
        elif self.model == User:
            instance = request.user
        else:
            raise FeedCloudBaseException(
                detail=gettext("Not implemented"),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return instance
