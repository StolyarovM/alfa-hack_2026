from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.company import Company
from app.models.application import Application
from app.models.verification import Verification
from app.schemas.application import ApplicationCreate
from app.api.routes.auth import current_user
from app.services.application_service import run_application

router = APIRouter()
def serialize(a, db):
    checks = db.query(Verification).filter_by(application_id=a.id).all()
    company = db.query(Company).filter_by(user_id=a.user_id).first()
    scoring_reason = None
    conditions = None
    if a.scoring_json:
        try:
            saved = json.loads(a.scoring_json)
            response = saved.get("response") or {}
            scoring_reason = response.get("причина")
            conditions = response.get("условия")
        except (TypeError, ValueError, AttributeError):
            scoring_reason = None
            conditions = None
    return {
        "id": a.id,
        "business_name": company.business_name if company else "",
        "inn": a.inn,
        "product_type": a.product_type,
        "requested_amount": a.requested_amount,
        "status": a.status,
        "outcome": a.outcome,
        "risk": a.risk,
        "scoring_reason": scoring_reason,
        "conditions": conditions,
        "created_at": a.created_at.isoformat(),
        "checks": [{"name": c.name, "status": c.status, "message": c.message} for c in checks],
    }

@router.post("")
async def create(payload: ApplicationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    # Компания впервые создаётся здесь — в момент оформления заявки, не при регистрации.
    company = db.query(Company).filter_by(user_id=user.id).first()
    if not company:
        company = Company(user_id=user.id, inn=payload.inn, business_name=payload.business_name.strip(), industry=payload.industry.strip())
        db.add(company)
    else:
        company.inn = payload.inn
        company.business_name = payload.business_name.strip()
        company.industry = payload.industry.strip()
    db.commit()
    db.refresh(company)
    a = Application(user_id=user.id, inn=payload.inn, age_ip=payload.age_ip, monthly_revenue=payload.monthly_revenue, monthly_credit_payments=payload.monthly_credit_payments, has_overdue=payload.has_overdue, has_collateral=payload.has_collateral, product_type=payload.product_type, requested_amount=payload.requested_amount, status="SUBMITTED", created_at=datetime.now(timezone.utc))
    db.add(a); db.commit(); db.refresh(a)
    await run_application(a, company, db)
    db.refresh(a)
    return serialize(a, db)

@router.get("")
def list_applications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(a, db) for a in db.query(Application).filter_by(user_id=user.id).order_by(Application.id.desc()).all()]

@router.get("/{application_id}")
def get_application(application_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter_by(id=application_id, user_id=user.id).first()
    if not a: raise HTTPException(404, "Заявка не найдена")
    return serialize(a, db)

@router.post("/{application_id}/retry")
async def retry(application_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter_by(id=application_id, user_id=user.id).first()
    if not a: raise HTTPException(404, "Заявка не найдена")
    company = db.query(Company).filter_by(user_id=user.id).first()
    if not company: raise HTTPException(400, "Сначала заполните данные компании в заявке")
    await run_application(a, company, db)
    db.refresh(a)
    return serialize(a, db)
