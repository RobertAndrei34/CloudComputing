from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    average_duration = Column(Integer, default=10)

class Counter(Base):
    __tablename__ = "counters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(String, default="OPEN")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="BOOKED")
    created_at = Column(DateTime, default=datetime.utcnow)

class QueueEntry(Base):
    __tablename__ = "queue_entries"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    queue_number = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    estimated_wait_time = Column(Integer, default=0)
    status = Column(String, default="WAITING")
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    source_event = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
