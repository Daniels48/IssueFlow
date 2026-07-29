from celery import Celery

from app.core.config import settings

rabbit_ = settings.rabbit
url_broker = f"amqp://{rabbit_.login}:{rabbit_.password}@{rabbit_.host}:{rabbit_.port}//"

celery_app = Celery("issueflow",broker=url_broker)
celery_app.conf.update(
    task_default_queue="emails",

    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    worker_enable_remote_control=False,
)