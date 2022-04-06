from django.urls import path
from utils import views as util_views

urlpatterns = [
    path(
        "staffs/permissions",
        util_views.AdminUpdatePermissionList.as_view(),
        name="permissions",
    ),
]
