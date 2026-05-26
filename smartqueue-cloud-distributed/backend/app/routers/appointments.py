from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.entities import Appointment, Service, User
from app.schemas.dto import AppointmentCreate, AppointmentRead
from app.services.events import publish_event

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentRead)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    appointment = Appointment(user_id=current_user.id, service_id=payload.service_id, scheduled_time=payload.scheduled_time, status="BOOKED")
    db.add(appointment); db.commit(); db.refresh(appointment)
    publish_event("appointment.created", {"user_id": current_user.id, "appointment_id": appointment.id, "service_name": service.name})
    return appointment

@router.get("/", response_model=list[AppointmentRead])
def list_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "ADMIN":
        return db.query(Appointment).all()
    return db.query(Appointment).filter(Appointment.user_id == current_user.id).all()

@router.patch("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role != "ADMIN" and appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this appointment")
    appointment.status = "CANCELLED"
    db.commit(); db.refresh(appointment)
    return appointment
