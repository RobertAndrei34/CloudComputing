from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.entities import Appointment, QueueEntry, Service, User
from app.schemas.dto import CallNextRequest, CheckInRequest, QueueEntryRead
from app.services.cache import get_queue_snapshot, invalidate_queue_snapshot, set_queue_snapshot
from app.services.events import publish_event

router = APIRouter(prefix="/queue", tags=["Queue"])

def serialize_entry(entry: QueueEntry):
    return {"id": entry.id, "appointment_id": entry.appointment_id, "queue_number": entry.queue_number, "position": entry.position, "estimated_wait_time": entry.estimated_wait_time, "status": entry.status}

def recompute_positions_and_eta(db: Session, service_id: int):
    service = db.query(Service).filter(Service.id == service_id).first()
    average_duration = service.average_duration if service else 10
    waiting_entries = (
        db.query(QueueEntry)
        .join(Appointment, Appointment.id == QueueEntry.appointment_id)
        .filter(Appointment.service_id == service_id)
        .filter(QueueEntry.status == "WAITING")
        .order_by(QueueEntry.queue_number.asc())
        .all()
    )
    for index, entry in enumerate(waiting_entries, start=1):
        entry.position = index
        entry.estimated_wait_time = max(index - 1, 0) * average_duration
    db.commit()
    invalidate_queue_snapshot(service_id)

@router.post("/check-in", response_model=QueueEntryRead)
def check_in(payload: CheckInRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(Appointment.id == payload.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role != "ADMIN" and appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to check in this appointment")
    if appointment.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cancelled appointments cannot check in")
    existing = db.query(QueueEntry).filter(QueueEntry.appointment_id == appointment.id).first()
    if existing:
        return existing
    last_entry = db.query(QueueEntry).order_by(QueueEntry.queue_number.desc()).first()
    next_number = 1 if not last_entry else last_entry.queue_number + 1
    queue_count = (
        db.query(QueueEntry)
        .join(Appointment, Appointment.id == QueueEntry.appointment_id)
        .filter(Appointment.service_id == appointment.service_id)
        .filter(QueueEntry.status == "WAITING")
        .count()
    )
    service = db.query(Service).filter(Service.id == appointment.service_id).first()
    avg = service.average_duration if service else 10
    entry = QueueEntry(appointment_id=appointment.id, queue_number=next_number, position=queue_count + 1, estimated_wait_time=queue_count * avg, status="WAITING")
    appointment.status = "CHECKED_IN"
    db.add(entry); db.commit(); db.refresh(entry)
    recompute_positions_and_eta(db, appointment.service_id)
    db.refresh(entry)
    publish_event("queue.checked_in", {"user_id": appointment.user_id, "appointment_id": appointment.id, "queue_number": entry.queue_number})
    return entry

@router.get("/{service_id}", response_model=list[QueueEntryRead])
def get_queue(service_id: int, db: Session = Depends(get_db)):
    cached = get_queue_snapshot(service_id)
    if cached is not None:
        return cached
    entries = (
        db.query(QueueEntry)
        .join(Appointment, Appointment.id == QueueEntry.appointment_id)
        .filter(Appointment.service_id == service_id)
        .order_by(QueueEntry.position.asc())
        .all()
    )
    data = [serialize_entry(entry) for entry in entries]
    set_queue_snapshot(service_id, data)
    return data

@router.post("/call-next", response_model=QueueEntryRead)
def call_next(payload: CallNextRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    entry = (
        db.query(QueueEntry)
        .join(Appointment, Appointment.id == QueueEntry.appointment_id)
        .filter(Appointment.service_id == payload.service_id)
        .filter(QueueEntry.status == "WAITING")
        .order_by(QueueEntry.queue_number.asc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No waiting users in queue")
    entry.status = "CALLED"
    appointment = db.query(Appointment).filter(Appointment.id == entry.appointment_id).first()
    appointment.status = "IN_PROGRESS"
    db.commit(); db.refresh(entry)
    recompute_positions_and_eta(db, payload.service_id)
    publish_event("queue.user_called", {"user_id": appointment.user_id, "appointment_id": appointment.id, "queue_number": entry.queue_number})
    return entry

@router.patch("/{entry_id}/complete", response_model=QueueEntryRead)
def complete_service(entry_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    entry.status = "DONE"
    appointment = db.query(Appointment).filter(Appointment.id == entry.appointment_id).first()
    service_id = None
    if appointment:
        appointment.status = "COMPLETED"
        service_id = appointment.service_id
    db.commit(); db.refresh(entry)
    if service_id:
        recompute_positions_and_eta(db, service_id)
    if appointment:
        publish_event("queue.service_completed", {"user_id": appointment.user_id, "appointment_id": appointment.id, "queue_number": entry.queue_number})
    return entry
