from pydantic import BaseModel

from app.infrastructure.rabbit.publisher import RabbitPublisher


class EventPublisher:
    @staticmethod
    async def publish(event: BaseModel) -> None:
        await RabbitPublisher.publish(event)


publisher = EventPublisher()