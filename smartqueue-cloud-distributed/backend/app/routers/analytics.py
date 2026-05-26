from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.entities import Appointment, QueueEntry, Service, User
from app.schemas.dto import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users_count = db.query(User).count()
    services_count = db.query(Service).count()
    appointments_count = db.query(Appointment).count()
    waiting_count = db.query(QueueEntry).filter(QueueEntry.status == "WAITING").count()
    called_count = db.query(QueueEntry).filter(QueueEntry.status == "CALLED").count()
    completed_count = db.query(QueueEntry).filter(QueueEntry.status == "DONE").count()
    avg_wait = db.query(func.avg(QueueEntry.estimated_wait_time)).scalar()
    return AnalyticsSummary(users_count=users_count, services_count=services_count, appointments_count=appointments_count, waiting_count=waiting_count, called_count=called_count, completed_count=completed_count, average_wait_time=round(float(avg_wait or 0), 2))

@router.get("/service-load")
def service_load(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.query(Service.id, Service.name, func.count(Appointment.id).label("appointments")).outerjoin(Appointment, Appointment.service_id == Service.id).group_by(Service.id, Service.name).all()
    return [{"service_id": row.id, "service_name": row.name, "appointments": row.appointments} for row in rows]
