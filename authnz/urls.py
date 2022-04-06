from django.urls import path, re_path

from authnz import views as authnz_views


urlpatterns = [
    path(
        "users/register", authnz_views.UserRegisterEmailView.as_view(), name="register"
    ),
    path("users/login", authnz_views.UserLoginEmailView.as_view(), name="login"),
    path(
        "users/refresh-token",
        authnz_views.UserRefreshTokenView.as_view(),
        name="refresh_token",
    ),
    path(
        "users/my_profile", authnz_views.UserMyProfileView.as_view(), name="my_profile"
    ),
    re_path(
        "^users/approve_email/(?P<uidb64>[0-9A-Za-z_\-']+)/"
        "(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})$",
        authnz_views.UserConfirmEmailView.as_view(),
        name="approve_email",
    ),
]
