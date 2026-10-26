import json
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.company import Company
from app.models.application import Application
from app.models.verification import Verification
from app.models.scoring_result import ScoringResult
from app.schemas.application import ApplicationCreate
from app.api.routes.auth import current_user
from app.services.application_service import run_application


router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


def serialize(a: Application, db: Session) -> dict:
    checks = (
        db.query(Verification)
        .filter_by(application_id=a.id)
        .all()
    )

    return {
        "id": a.id,
        "product_type": a.product_type,
        "requested_amount": a.requested_amount,
        "status": a.status,
        "outcome": a.outcome,
        "risk": a.risk,
        "created_at": a.created_at.isoformat(),
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "message": check.message,
            }
            for check in checks
        ],
    }


@router.post("")
async def create(
    payload: ApplicationCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if payload.inn != user.inn:
        raise HTTPException(
            status_code=400,
            detail="ИНН должен совпадать с ИНН профиля в демо-версии",
        )

    company = (
        db.query(Company)
        .filter_by(user_id=user.id)
        .first()
    )

    if not company:
        company = Company(user_id=user.id, inn=user.inn)
        db.add(company)
        db.commit()
        db.refresh(company)

    application = Application(
        user_id=user.id,
        inn=payload.inn,
        age_ip=payload.age_ip,
        monthly_revenue=payload.monthly_revenue,
        monthly_credit_payments=payload.monthly_credit_payments,
        has_overdue=payload.has_overdue,
        has_collateral=payload.has_collateral,
        product_type=payload.product_type,
        requested_amount=payload.requested_amount,
        status="SUBMITTED",
        created_at=datetime.now(timezone.utc),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    await run_application(application, company, db)
    db.refresh(application)

    return serialize(application, db)


@router.get("")
def list_applications(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    applications = (
        db.query(Application)
        .filter_by(user_id=user.id)
        .order_by(Application.id.desc())
        .all()
    )

    return [serialize(application, db) for application in applications]


@router.get("/{application_id}")
def get_application(
    application_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter_by(id=application_id, user_id=user.id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    return serialize(application, db)


@router.post("/{application_id}/retry")
async def retry(
    application_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter_by(id=application_id, user_id=user.id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    company = (
        db.query(Company)
        .filter_by(user_id=user.id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Профиль компании не найден",
        )

    await run_application(application, company, db)
    db.refresh(application)

    return serialize(application, db)


@router.post("/{application_id}/chat")
async def application_chat(
    application_id: int,
    payload: ChatRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    # Проверяем принадлежность заявки текущему пользователю.
    application = (
        db.query(Application)
        .filter_by(id=application_id, user_id=user.id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    company = (
        db.query(Company)
        .filter_by(user_id=user.id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Профиль компании не найден",
        )

    message = payload.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Введите вопрос",
        )

    # Берём причину из ранее сохранённого результата скоринга.
    reason = None

    if application.scoring_json:
        try:
            saved = json.loads(application.scoring_json)
            result = saved.get("response", {})

            if isinstance(result, dict):
                reason = result.get("причина") or result.get("reason")

        except (json.JSONDecodeError, TypeError, AttributeError):
            reason = None

    revenue = float(application.monthly_revenue or 0)
    credit_payments = float(application.monthly_credit_payments or 0)

    debt_load = (
        credit_payments / revenue * 100
        if revenue > 0
        else 0.0
    )

    # Эти признаки соответствуют полям скорингового сервиса.
    chat_payload = {
        "client_name": user.username,
        "Тип_продукта": application.product_type,
        "Возраст_ИП": int(application.age_ip),
        "Срок_работы_мес": int(company.business_age_months or 0),
        "Выручка_в_месяц": int(revenue),
        "Оборот_в_месяц": int(company.monthly_turnover or 0),
        "Сотрудники": int(company.employees or 0),
        "Долговая_нагрузка_процент": round(debt_load, 2),
        "Действующие_кредиты": int(company.active_credits or 0),
        "Просрочки": int(bool(application.has_overdue)),
        "Отрасль": str(company.industry or "Не указана"),
        "Счет_в_банке_мес": int(company.bank_account_months or 0),
        "LTV_залога": 50 if application.has_collateral else 0,
        "Сумма_кредита": int(application.requested_amount),
        "решение": application.outcome or application.status,
        "риск": (
            float(application.risk)
            if application.risk is not None
            else None
        ),
        "причина": reason,
        "user_message": message,
    }

    chat_url = os.getenv(
        "SCORING_CHAT_URL",
        "http://scoring-service:9562/chat",
    )

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(180.0)
        ) as client:
            response = await client.post(
                chat_url,
                json=chat_payload,
            )
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Модель не успела подготовить ответ. Попробуйте ещё раз.",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Сервис ИИ вернул ошибку при обработке вопроса.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Сервис ИИ недоступен. Проверьте запуск "
                "scoring-service и Ollama."
            ),
        )

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="Сервис ИИ вернул некорректный ответ.",
        )

    reply = data.get("reply")

    if not isinstance(reply, str) or not reply.strip():
        raise HTTPException(
            status_code=502,
            detail="Модель вернула пустой ответ.",
        )

    return {"reply": reply.strip()}