from django.utils.translation import gettext
from rest_framework import permissions, status

from utils.exceptions import FeedCloudBaseException


class StaffPermission(permissions.BasePermission):
    """
    Global permission check for Staff

    Is super user or has perm for this api

    perm will create from api /staff/permissions
    """

    def has_permission(self, request, view):
        if (
            request.user.is_staff
            and request.user.has_perm(f"auth.{view.__class__.__name__}")
        ) or request.user.is_superuser:
            return True
        return False


def check_create_permission(request):
    if request.user.is_superuser:
        return True
    else:
        raise FeedCloudBaseException(
            detail=gettext("No Permission to create."), code=status.HTTP_403_FORBIDDEN
        )


def check_update_permission(request, instance):
    if request.user.is_superuser:
        return True
    elif request.user.is_staff and request.user.has_perm(
        f"auth.{request.parser_context['view'].__class__.__name__}"
    ):
        return True
    elif hasattr(instance, "creator") and instance.creator == request.user:
        return True
    else:
        raise FeedCloudBaseException(
            detail=gettext("No Permission to update."), code=status.HTTP_403_FORBIDDEN
        )


def check_delete_permission(request, instance):
    if request.user.is_superuser:
        return True
    elif request.user.is_staff and request.user.has_perm(
        f"auth.{request.parser_context['view'].__class__.__name__}"
    ):
        return True
    else:
        raise FeedCloudBaseException(
            detail=gettext("No Permission to delete."), code=status.HTTP_403_FORBIDDEN
        )
