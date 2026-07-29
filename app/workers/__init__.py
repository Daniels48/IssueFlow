from .celery.mail import send_email
from .celery.main import celery_app
from .celery.tasks import send_email_task