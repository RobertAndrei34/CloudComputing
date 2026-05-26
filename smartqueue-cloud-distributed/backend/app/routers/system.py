import os
import pika
from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal
from app.schemas.dto import HealthStatus
from app.services.cache import redis_ping

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health", response_model=HealthStatus)
def health():
    database = "down"
    redis = "down"
    rabbitmq = "down"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        database = "up"
    except Exception:
        pass
    try:
        if redis_ping():
            redis = "up"
    except Exception:
        pass
    try:
        connection = pika.BlockingConnection(pika.URLParameters(os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")))
        connection.close()
        rabbitmq = "up"
    except Exception:
        pass
    return HealthStatus(api="up", database=database, redis=redis, rabbitmq=rabbitmq)
