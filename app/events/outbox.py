from app.events.base import Event_OutBox
from app.infrastructure.db.models import OutboxEvent


class OutboxFactory:

    @staticmethod
    def from_event(event: Event_OutBox) -> OutboxEvent:
        return OutboxEvent(
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            occurred_at=event.occurred_at,
            payload=event.model_dump(mode="json"),
        )