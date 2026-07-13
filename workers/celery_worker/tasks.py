from workers.celery.app import celery_app


@celery_app.task(name="notifications.issue_created")
def issue_created_notification(
    issue_public_id: str,
    project_public_id: str,
    title: str,
):
    print(issue_public_id)

    # email

    # push

    # telegram

    # discord