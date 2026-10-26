
from pathlib import Path
import json
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "companies.json"
def company_for_inn(inn: str) -> dict:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if inn in data: return {"inn": inn, **data[inn]}
    # Детерминированный fallback для произвольного тестового ИНН.
    seed = sum(int(c) for c in inn)
    industries = ["Онлайн-торговля", "Услуги", "Производство", "Общественное питание"]
    return {"inn":inn,"business_type":"ИП","business_age_months":12 + seed % 60,"industry":industries[seed % len(industries)],"monthly_turnover":250000 + (seed % 8) * 50000,"employees":seed % 10,"active_credits":seed % 3,"bank_account_months":6 + seed % 48,"registry_status":"ACTIVE"}
