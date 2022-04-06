from rest_framework import decorators, views
from rest_framework.permissions import IsAuthenticated

from utils.responses import SuccessResponse
from utils.permissions import StaffPermission
from utils.tasks import update_api_permissions


@decorators.permission_classes((IsAuthenticated, StaffPermission))
class AdminUpdatePermissionList(views.APIView):
    """
    post:
        Admin update permission list

        Update the list of permissions in django

        You can add permissions to any user by django admin

    """

    def post(self, request, *args, **kwargs):
        update_api_permissions.apply_async()
        return SuccessResponse({})
