import re
import types

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import get_resolver

from feedcloud.celery import app


@app.task(name="update_api_permissions")
def update_api_permissions():
    """
    Add views names as permissions to use with django admin permission

    :return:
    """
    view_black_list = (
        "UserConfirmEmailView",
        "UserRefreshTokenView",
        "UserMyProfileView",
        "UserLoginEmailView",
        "UserRegisterEmailView",
        "SchemaView",
    )
    http_method_names = (
        "get",
        "post",
        "put",
        "patch",
        "delete",
    )
    view_names = []
    for view in get_resolver().reverse_dict.keys():
        if (
            isinstance(view, types.FunctionType)
            and (view_class_name := view.view_class.__name__) not in view_black_list
        ):
            view_names.extend(
                [
                    f"{method.title()}{view_class_name}"
                    for method in http_method_names
                    if hasattr(view.view_class, method)
                ]
            )
    content_type = ContentType.objects.get_for_model(User)
    for view in view_names:
        name_space = " ".join(re.findall("[A-Z][^A-Z]*", view))
        Permission.objects.get_or_create(
            name=name_space, codename=view, content_type=content_type
        )
