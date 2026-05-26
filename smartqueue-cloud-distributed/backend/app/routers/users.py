from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.entities import User
from app.schemas.dto import UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).all()
