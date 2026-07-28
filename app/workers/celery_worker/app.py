from celery import Celery

from app.core.config import settings

rabbit_ = settings.rabbit
url_broker = f"amqp://{rabbit_.login}:{rabbit_.password}@{rabbit_.host}:{rabbit_.port}//"

celery_app = Celery("issueflow",broker=url_broker)