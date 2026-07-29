import smtplib
from email.message import EmailMessage


def send_email(to: str,subject: str,body: str):
    msg = EmailMessage()

    msg["From"] = "noreply@issueflow.local"
    msg["To"] = to
    msg["Subject"] = subject

    msg.set_content(body)

    with smtplib.SMTP("mailhog",1025) as smtp:
        smtp.send_message(msg)