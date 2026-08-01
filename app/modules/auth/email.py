from fastapi.templating import Jinja2Templates

from app.infrastructure.db.models import User
from app.infrastructure.reddis.verify_email import VerifyEmailCache
from app.workers.celery.tasks import send_email_task

templates = Jinja2Templates(directory="app/web/templates/emails")



class EmailVerificationService:
    @classmethod
    async def send(cls, user: User):
        code = await VerifyEmailCache.create(user.public_id)
        html = templates.get_template("verify_email.html").render(
            username=user.username,
            code=code,
        )
        
        send_email_task.delay(user.email, user.username, html)