import json
import os
import time
import pika

EXCHANGE_NAME = "smartqueue.events"
QUEUE_NAME = "smartqueue.notifications"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def _connection_with_retry(retries: int = 10, delay: float = 2.0):
    last_error = None
    for _ in range(retries):
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            return pika.BlockingConnection(params)
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error

def setup_broker(channel):
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="appointment.created")
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="queue.checked_in")
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="queue.user_called")
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="queue.service_completed")

def publish_event(event_type: str, payload: dict):
    try:
        connection = _connection_with_retry(retries=3, delay=1)
        channel = connection.channel()
        setup_broker(channel)
        body = json.dumps({"event_type": event_type, "payload": payload})
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=event_type,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        connection.close()
        return True
    except Exception as exc:
        print(f"[events] Could not publish {event_type}: {exc}")
        return False
