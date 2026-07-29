from app.workers.celery.mail import send_email
from app.workers.celery.main import celery_app


@celery_app.task(name="send_email")
def send_email_task(email: str,subject: str,body: str):
    send_email(to=email, subject=subject, body=body)