from sqlalchemy.orm import Session
from app.models.entities import Notification

def create_notification(db: Session, user_id: int, title: str, message: str, source_event: str | None = None) -> Notification:
    notification = Notification(user_id=user_id, title=title, message=message, read=False, source_event=source_event)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
