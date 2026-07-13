from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "issueflow",
    broker=f"amqp://{settings.rabbit.login}:{settings.rabbit.password}@{settings.rabbit.host}:{settings.rabbit.port}//",
)