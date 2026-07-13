from aio_pika.abc import AbstractIncomingMessage

from app.infrastructure.rabbit.events import IssueCreatedEvent
from workers.celery.app import celery_app


async def issue_created_handler(
    message: AbstractIncomingMessage,
):
    event = IssueCreatedEvent.model_validate_json(message.body)

    celery_app.send_task(
        "notifications.issue_created",
        kwargs={
            "issue_public_id": str(event.issue_public_id),
            "project_public_id": str(event.project_public_id),
            "title": event.title,
        },
    )