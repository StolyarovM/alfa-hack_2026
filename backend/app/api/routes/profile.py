from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.company import Company
from app.models.verification import Verification
from app.api.routes.auth import current_user

router = APIRouter()

@router.get("/profile")
def profile(user: User = Depends(current_user)):
    # Профиль содержит данные человека. Компания здесь не создаётся и ИНН не требуется.
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "phone": user.phone}

@router.get("/profile/checks")
def previous_checks(user: User = Depends(current_user), db: Session = Depends(get_db)):
    from app.models.application import Application
    ids = [a.id for a in db.query(Application).filter_by(user_id=user.id).all()]
    if not ids:
        return []
    return [{"name": v.name, "status": v.status} for v in db.query(Verification).filter(Verification.application_id.in_(ids)).all()]
