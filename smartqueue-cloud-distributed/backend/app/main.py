import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.entities import Service, User
from app.routers import analytics, appointments, auth, notifications, queue, services, system, users

def init_database_with_retry():
    retries = 20
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(2)

init_database_with_retry()

app = FastAPI(title="SmartQueue Cloud API", version="3.0.0", description="Distributed MVP API for appointments, virtual queues, Redis caching, RabbitMQ events and notification worker processing.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(queue.router)
app.include_router(notifications.router)
app.include_router(analytics.router)
app.include_router(system.router)

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if db.query(User).count() == 0:
        db.add(User(name="Demo User", email="user@demo.com", password_hash=hash_password("user123"), role="USER"))
        db.add(User(name="Demo Admin", email="admin@demo.com", password_hash=hash_password("admin123"), role="ADMIN"))
    if db.query(Service).count() == 0:
        db.add(Service(name="Student Secretariat", description="Academic documents and requests", average_duration=8))
        db.add(Service(name="Medical Appointment", description="Basic consultation queue", average_duration=12))
        db.add(Service(name="City Hall Desk", description="Public administration requests", average_duration=15))
    db.commit(); db.close()

@app.get("/")
def root():
    return {"message": "SmartQueue Cloud API is running", "docs": "/docs", "openapi": "/openapi.json", "health": "/system/health"}
