
import json
import logging

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.company import Company
from app.models.verification import Verification
from app.models.scoring_result import ScoringResult
from app.services.scoring_client import score_application
from app.integrations.mock_client import get_company_data, run_check


logger = logging.getLogger(__name__)


async def run_application(
    a: Application,
    company: Company,
    db: Session,
):
    """Выполняет проверки компании и сохраняет результат скоринга."""

    try:
        # Удаляем результаты предыдущего запуска проверок.
        db.query(Verification).filter_by(
            application_id=a.id
        ).delete()

        a.status = "DATA_CHECK"
        db.commit()

        remote = await get_company_data(a.inn)

        checks = [
            ("Реестры", "registry"),
            ("Кредитная история", "credit-history"),
            ("Финансовые данные", "financial"),
        ]

        for name, endpoint in checks:
            check_result = await run_check(endpoint, a.inn)

            db.add(
                Verification(
                    application_id=a.id,
                    name=name,
                    status=(
                        "PASSED"
                        if check_result.get("ok")
                        else "FAILED"
                    ),
                    message=check_result.get("message", ""),
                )
            )

        # Обновляем сведения из сервиса данных компании.
        if remote.get("business_age_months") is not None:
            company.business_age_months = int(
                remote["business_age_months"]
            )

        if remote.get("monthly_turnover") is not None:
            company.monthly_turnover = int(
                remote["monthly_turnover"]
            )

        if remote.get("employees") is not None:
            company.employees = int(remote["employees"])

        if remote.get("active_credits") is not None:
            company.active_credits = int(
                remote["active_credits"]
            )

        if remote.get("bank_account_months") is not None:
            company.bank_account_months = int(
                remote["bank_account_months"]
            )

        db.commit()

        a.status = "SCORING"
        db.commit()

        monthly_revenue = float(a.monthly_revenue or 0)
        monthly_payments = float(a.monthly_credit_payments or 0)

        debt_load = (
            monthly_payments / monthly_revenue * 100
            if monthly_revenue > 0
            else 0.0
        )

        scoring_payload = {
            "Тип_продукта": a.product_type,
            "Возраст_ИП": a.age_ip,
            "Срок_работы_мес": company.business_age_months,
            "Выручка_в_месяц": a.monthly_revenue,
            "Оборот_в_месяц": company.monthly_turnover,
            "Сотрудники": company.employees,
            "Долговая_нагрузка_процент": round(debt_load, 2),
            "Действующие_кредиты": company.active_credits,
            "Просрочки": 1 if a.has_overdue else 0,
            "Отрасль": company.industry,
            "Счет_в_банке_мес": company.bank_account_months,
            "LTV_залога": 50 if a.has_collateral else 0,
            "Сумма_кредита": a.requested_amount,
        }

        result, mode = await score_application(scoring_payload)

        risk = result.get("риск")
        decision = str(result.get("решение") or "").strip()
        reason = result.get("причина")

        if not decision:
            raise ValueError(
                "Скоринговый сервис вернул пустое решение."
            )

        # Не меняем отказ модели на условное одобрение.
        if (
            risk is not None
            and 0.25 <= float(risk) < 0.50
            and "отказ" not in decision.lower()
        ):
            decision = "Одобрено на других условиях"
            result["условия"] = (
                "Рекомендуется рассмотреть меньшую сумму кредита "
                "или предоставить дополнительное обеспечение. "
                "Условия требуют подтверждения кредитором."
            )
            result["решение"] = decision

        # Сохраняем причину отказа, если сервис её вернул.
        if reason is not None:
            result["причина"] = reason

        a.risk = risk
        a.outcome = decision
        a.scoring_json = json.dumps(
            {
                "mode": mode,
                "request": scoring_payload,
                "response": result,
            },
            ensure_ascii=False,
        )

        db.add(
            ScoringResult(
                application_id=a.id,
                risk=risk,
                decision=decision,
                model_version=mode,
                request_json=json.dumps(
                    scoring_payload,
                    ensure_ascii=False,
                ),
                response_json=json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            )
        )

        a.status = "RESULT_READY"
        db.commit()

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Application processing failed: application_id=%s, inn=%s",
            a.id,
            a.inn,
        )

        try:
            a.status = "SCORING_ERROR"
            a.outcome = None

            db.add(
                Verification(
                    application_id=a.id,
                    name="Обработка заявки",
                    status="FAILED",
                    message=(
                        "Не удалось завершить проверки: "
                        f"{type(exc).__name__}"
                    ),
                )
            )

            db.commit()

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to save application error status: application_id=%s",
                a.id,
            )
