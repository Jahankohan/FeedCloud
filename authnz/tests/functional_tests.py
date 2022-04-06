import re

import pytest
from django.urls import reverse
from django.conf import settings

from authnz.models import User
from authnz.utils import generate_token


@pytest.fixture
def user_sample_data():
    return {
        "email": "test@test.com",
        "password": "Str0n5Pass",
    }


@pytest.fixture
def user_sample(user_sample_data):
    user = User.register_user(**user_sample_data)
    return user


@pytest.fixture
def user_sample_with_approved_email(user_sample):
    user_sample.confirm_email()
    return user_sample


@pytest.fixture
def user_authorize_header(user_sample_with_approved_email):
    return {
        "HTTP_AUTHORIZATION": f"JWT {generate_token(user_sample_with_approved_email)}"
    }


class TestUser:
    @pytest.mark.django_db
    def test_user_register_correctly(self, user_sample_data, user_sample):
        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.username == user_sample_data["email"]
        assert user.email == user_sample_data["email"]
        assert user.check_password(user_sample_data["password"])

    @pytest.mark.django_db
    def test_user_register_multi_time_should_fail(self, client, user_sample_data):
        url = reverse("register")
        for i in range(settings.MAX_EMAIL_SEND_COUNT):
            resp = client.post(url, user_sample_data, content_type="application/json")
            assert resp.status_code == 201
        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 403

    @pytest.mark.django_db
    def test_user_register_weak_password(self, client):
        url = reverse("register")
        data = {"email": "test@test.com", "password": "12345678"}
        resp = client.post(url, data, content_type="application/json")
        assert resp.status_code == 400
        assert not resp.json()["success"]
        assert resp.json()["message"].get("password")

    @pytest.mark.django_db
    def test_register_user_success_functionality(
        self, client, user_sample_data, mailoutbox
    ):
        url = reverse("register")
        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 201
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == "Confirm your email"
        assert mail.to == [user_sample_data["email"]]

    @pytest.mark.django_db
    def test_user_login_without_email_confirm_should_fail(
        self, user_sample_data, user_sample, client, mailoutbox
    ):
        url = reverse("login")
        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 400
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == "Confirm your email"
        assert mail.to == [user_sample.email]

    @pytest.mark.django_db
    def test_user_multi_failed_login_should_fail_throttle(
        self, client, user_sample_data, user_sample_with_approved_email
    ):
        url = reverse("login")
        user_sample_data["password"] = "wrongpass"
        for i in range(10):  # UserRegisterEmailView throttle_rate
            resp = client.post(url, user_sample_data, content_type="application/json")
            assert resp.status_code == 400
        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 429

    @pytest.mark.django_db
    def test_user_email_confirmation_process(
        self, user_sample_data, user_sample, client, mailoutbox
    ):
        url = reverse("login")
        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 400
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == "Confirm your email"
        assert mail.to == [user_sample.email]
        link = re.findall(
            r"http://testserver/users/approve_email/"
            "[0-9A-Za-z_]+/[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32}",
            mail.alternatives[0][0],
        )
        assert len(link) == 1
        resp = client.get(link[0])
        assert resp.status_code == 200

        resp = client.get(link[0])
        assert resp.status_code == 400

        resp = client.post(url, user_sample_data, content_type="application/json")
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_login_response_success(
        self, client, user_sample_data, user_sample_with_approved_email
    ):
        url = reverse("login")
        resp = client.post(url, user_sample_data, content_type="application/json")
        resp_json = resp.json()
        resp_keys = (
            "data",
            "message",
            "show_type",
            "current_time",
            "success",
            "index",
            "total",
        )
        assert all([key in resp_keys for key in resp_json.keys()])
        assert all([key in ("token", "user") for key in resp_json["data"].keys()])

    @pytest.mark.django_db
    def test_refresh_token_success(self, client, user_authorize_header):
        url = reverse("refresh_token")
        resp = client.get(url, **user_authorize_header)
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_get_profile(self, client, user_sample_data, user_authorize_header):
        url = reverse("my_profile")
        resp = client.get(url, **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()
        resp_keys = (
            "data",
            "message",
            "show_type",
            "current_time",
            "success",
            "index",
            "total",
        )

        assert all([key in resp_keys for key in resp_json.keys()])
        assert resp_json["data"]["email"] == user_sample_data["email"]
        assert resp_json["data"]["email_confirmed"]
        assert resp_json["data"]["first_name"] == ""
        assert resp_json["data"]["last_name"] == ""

    @pytest.mark.django_db
    def test_update_profile(self, client, user_sample_data, user_authorize_header):
        url = reverse("my_profile")
        data = {
            "first_name": "my new first name",
            "last_name": "my new last name",
        }
        resp = client.put(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["data"]["email"] == user_sample_data["email"]
        assert resp_json["data"]["email_confirmed"]
        assert resp_json["data"]["first_name"] == data["first_name"]
        assert resp_json["data"]["last_name"] == data["last_name"]

        user = User.objects.first()
        assert user.first_name == data["first_name"]
        assert user.last_name == data["last_name"]

        # remove fist_name, last name
        data = {
            "first_name": "",
            "last_name": "",
        }
        resp = client.put(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["data"]["first_name"] == ""
        assert resp_json["data"]["last_name"] == ""
