from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from authnz import urls as authnz_urls
from feed import urls as feed_urls
from utils import urls as utils_urls


schema_view = get_schema_view(
    openapi.Info(title="FeedCloud API", default_version="v1"),
    url="http://localhost:8008" if not settings.DEBUG else None,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    re_path(
        "^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("", include(authnz_urls)),
    path("", include(feed_urls)),
    path("", include(utils_urls)),
]


handler404 = "utils.responses.handler404"
handler500 = "utils.responses.handler500"
