import httpx
import pytest
from app.services.scoring_client import score_application


@pytest.mark.asyncio
async def test_demo_scoring_returns_contract(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "scoring_api_url", "")
    result, mode = await score_application({"Просрочки": 0, "Долговая_нагрузка_процент": 10, "Срок_работы_мес": 24})
    assert 0 <= result["риск"] <= 1
    assert "решение" in result
    assert mode == "demo-fallback"


@pytest.mark.asyncio
async def test_external_regular_response(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "scoring_api_url", "https://bless.fxtun.dev/score")

    async def handler(request):
        assert request.method == "POST"
        return httpx.Response(200, json={"риск": 0.24, "решение": "Одобрено (низкий риск)"})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs))
    result, mode = await score_application({"Тип_продукта": "Оборотный"})
    assert result == {"риск": 0.24, "решение": "Одобрено (низкий риск)"}
    assert mode == "external"


@pytest.mark.asyncio
async def test_external_stop_factor_response(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "scoring_api_url", "https://bless.fxtun.dev/score")

    async def handler(request):
        return httpx.Response(200, json={"ds": "Отказ", "reason": "Стоп-фактор: деятельность < 3 мес."})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs))
    result, mode = await score_application({"Тип_продукта": "Оборотный"})
    assert result == {"риск": None, "решение": "Отказ", "причина": "Стоп-фактор: деятельность < 3 мес."}
    assert mode == "external"
