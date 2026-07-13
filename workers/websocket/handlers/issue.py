from aio_pika.abc import AbstractIncomingMessage

from app.infrastructure.rabbitmq.events import IssueCreatedEvent
from workers.websocket.manager import manager


async def issue_created_handler(message: AbstractIncomingMessage) -> None:
    event = IssueCreatedEvent.model_validate_json(message.body)

    await manager.send_to_user(
        event.reporter_public_id,
        {
            "type": "issue.created",
            "issue_public_id": str(event.issue_public_id),
            "title": event.title,
        },
    )

    if event.assignee_public_id:
        await manager.send_to_user(
            event.assignee_public_id,
            {
                "type": "issue.created",
                "issue_public_id": str(event.issue_public_id),
                "title": event.title,
            },
        )