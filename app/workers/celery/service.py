from fastapi.templating import Jinja2Templates

from app.infrastructure.db.models import User
from app.workers.celery.tasks import send_email_task


templates = Jinja2Templates(directory="app/web/templates/emails")


class BaseEmailService:
    TEMPLATE: str
    CACHE = None

    @classmethod
    async def send(cls, user: User) -> None:
        code = await cls.CACHE.create(user.public_id)
        html = templates.get_template(cls.TEMPLATE).render(username=user.username,code=code)
        send_email_task.delay(user.email,user.username,html)
