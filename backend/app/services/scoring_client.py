
import httpx

from app.core.config import settings


async def score_application(payload: dict) -> tuple[dict, str]:
    """
    Вызывает внешний сервис скоринга и нормализует его ответы.

    Поддерживаемые форматы:
    1. {"решение": "...", "риск": 0.11, "причина": null}
    2. {"решение": "Отказ", "риск": null, "причина": "..."}
    3. {"ds": "Отказ", "reason": "..."}
    """

    scoring_url = settings.scoring_api_url.strip()

    if not scoring_url:
        raise RuntimeError(
            "Сервис скоринга не настроен. "
            "Проверьте параметр SCORING_API_URL."
        )

    async with httpx.AsyncClient(
        timeout=settings.scoring_timeout_seconds
    ) as client:
        response = await client.post(
            scoring_url,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        raise ValueError(
            "Ответ скоринговой модели должен быть JSON-объектом."
        )

    # Формат ответа при срабатывании стоп-фактора.
    if "ds" in data:
        decision = str(data.get("ds") or "Отказ")
        reason_value = data.get("reason")
        reason = (
            str(reason_value)
            if reason_value is not None
            else "Сработал стоп-фактор скоринга."
        )

        return {
            "риск": None,
            "решение": decision,
            "причина": reason,
        }, "external"

    # Обычный ответ модели или нормализованный ответ с отказом.
    if "решение" not in data:
        raise ValueError(
            "В ответе скоринговой модели отсутствует поле 'решение'."
        )

    decision = str(data.get("решение") or "").strip()

    if not decision:
        raise ValueError(
            "Скоринговая модель вернула пустое поле 'решение'."
        )

    raw_risk = data.get("риск")
    risk = None

    if raw_risk is not None:
        try:
            risk = float(raw_risk)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Поле 'риск' должно быть числом или null."
            ) from exc

        if not 0 <= risk <= 1:
            raise ValueError(
                "Поле 'риск' должно быть в диапазоне от 0 до 1."
            )

    reason_value = data.get("причина")
    reason = (
        str(reason_value)
        if reason_value is not None
        else None
    )

    # Отсутствие риска допустимо для отказа по стоп-фактору.
    if risk is None and "отказ" not in decision.lower():
        raise ValueError(
            "Скоринговая модель не вернула риск "
            "для решения, отличного от отказа."
        )

    normalized = {
        "риск": risk,
        "решение": decision,
        "причина": reason,
    }

    return normalized, "external"
