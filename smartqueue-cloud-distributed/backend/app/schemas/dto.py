from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "USER"

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    average_duration: int = 10

class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class AppointmentCreate(BaseModel):
    service_id: int
    scheduled_time: datetime

class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    service_id: int
    scheduled_time: datetime
    status: str

class CheckInRequest(BaseModel):
    appointment_id: int

class CallNextRequest(BaseModel):
    service_id: int

class QueueEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    appointment_id: int
    queue_number: int
    position: int
    estimated_wait_time: int
    status: str

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    message: str
    read: bool
    source_event: Optional[str] = None
    created_at: datetime

class AnalyticsSummary(BaseModel):
    users_count: int
    services_count: int
    appointments_count: int
    waiting_count: int
    called_count: int
    completed_count: int
    average_wait_time: float

class HealthStatus(BaseModel):
    api: str
    database: str
    redis: str
    rabbitmq: str
