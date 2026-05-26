from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.entities import Service, User
from app.schemas.dto import ServiceCreate, ServiceRead

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/", response_model=ServiceRead)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = Service(name=payload.name, description=payload.description, average_duration=payload.average_duration)
    db.add(service); db.commit(); db.refresh(service)
    return service

@router.get("/", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()
