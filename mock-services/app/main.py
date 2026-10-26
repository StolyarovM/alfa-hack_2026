
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.company_data import company_for_inn
from app.verification_rules import check_result

app = FastAPI(title="Mock external services", version="0.1.0")
class CheckRequest(BaseModel):
    inn: str

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/api/v1/companies/{inn}")
def get_company(inn: str):
    if not inn.isdigit() or len(inn) not in (10,12): raise HTTPException(400, "Некорректный ИНН")
    return company_for_inn(inn)

@app.post("/api/v1/checks/{check_name}")
def run_check(check_name: str, request: CheckRequest):
    if check_name not in {"registry", "credit-history", "financial"}: raise HTTPException(404, "Неизвестная проверка")
    return check_result(check_name, request.inn)
