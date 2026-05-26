import json
import time
from sqlalchemy.exc import OperationalError
from app.database import Base, SessionLocal, engine
from app.models.entities import Notification
from app.services.events import QUEUE_NAME, _connection_with_retry, setup_broker

TITLES = {
    "appointment.created": "Appointment created",
    "queue.checked_in": "Check-in completed",
    "queue.user_called": "You have been called",
    "queue.service_completed": "Service completed",
}

def build_message(event_type: str, payload: dict) -> str:
    if event_type == "appointment.created":
        return f"Your appointment #{payload.get('appointment_id')} for {payload.get('service_name')} was created successfully."
    if event_type == "queue.checked_in":
        return f"You joined the queue. Your ticket number is {payload.get('queue_number')}."
    if event_type == "queue.user_called":
        return f"Ticket #{payload.get('queue_number')} has been called. Please go to the service desk."
    if event_type == "queue.service_completed":
        return f"Appointment #{payload.get('appointment_id')} was completed successfully."
    return "SmartQueue event received."

def init_db_with_retry():
    for attempt in range(20):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database unavailable for worker")

def handle_event(channel, method, properties, body):
    try:
        event = json.loads(body.decode("utf-8"))
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        user_id = payload.get("user_id")
        if user_id:
            db = SessionLocal()
            notification = Notification(
                user_id=user_id,
                title=TITLES.get(event_type, "SmartQueue notification"),
                message=build_message(event_type, payload),
                read=False,
                source_event=event_type,
            )
            db.add(notification)
            db.commit()
            db.close()
            print(f"[worker] notification created for user {user_id} from {event_type}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:
        print(f"[worker] error: {exc}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    init_db_with_retry()
    connection = _connection_with_retry(retries=30, delay=2)
    channel = connection.channel()
    setup_broker(channel)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_event)
    print("[worker] waiting for notification events")
    channel.start_consuming()

if __name__ == "__main__":
    main()
