from rest_framework import generics

from utils.responses import SuccessResponse
from utils.permissions import check_delete_permission


class DeleteView(generics.DestroyAPIView):
    """
    Delete instance
    """

    def delete(self, request, instance_id: int, *args, **kwargs):
        instance = self.model.objects.get(id=instance_id)
        check_delete_permission(request, instance)
        instance.delete()
        return SuccessResponse({}, status=204)
