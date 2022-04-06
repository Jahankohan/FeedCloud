from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from authnz.permissions import increase_send_email_count
from feedcloud.celery import app


@app.task(name="send_email")
def send_email(email, template_context):
    """
    sends email

    :return:
    """
    """
            Sends email verification
            :param request:
            :return:
            """
    subject = "Confirm your email"
    message = render_to_string(
        "authnz/email_verification.html",
        template_context,
    )
    resp = send_mail(
        subject=subject,
        message="",
        from_email=settings.EMAILS_LIST.get("support"),
        recipient_list=[email],
        html_message=message,
    )
    increase_send_email_count(email)
