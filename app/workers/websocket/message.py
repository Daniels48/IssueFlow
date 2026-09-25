from app.events import Event
from app.workers.websocket.schemas import EventEnvelope, WebSocketEvent


def create_message(event: Event, envelope: EventEnvelope) -> dict:
    message = WebSocketEvent(
        event_type=envelope.event_type,
        payload=event.model_dump(
            mode="json",
            exclude={"aggregate_id"},
        ),
    )

    return {
        "event_id": str(envelope.event_id),
        "message": message.model_dump(mode="json"),
    }