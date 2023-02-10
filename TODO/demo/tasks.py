
from django.core.mail import send_mail
from celery import shared_task
from celery.utils.log import get_task_logger
from TODO import settings
logger = get_task_logger(__name__)


@shared_task()
def send_email_task(email_address, otp):
    logger.info("Task Started")

    msg = f"Hello Welcome to TODO App. YOur otp is {otp}"
    logger.info("sending mail")

    send_mail(
        "Welcome to TODO APP.",
        msg,
        settings.EMAIL_HOST_USER,
        [email_address],
        fail_silently=False,
    )
    logger.info("TAsk ended")
    return {'status': True}

