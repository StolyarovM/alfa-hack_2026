
from fastapi import APIRouter, Depends
from app.api.routes.auth import current_user
from app.models.user import User
router = APIRouter()
PRODUCTS = [
 {"id":"working-capital","name":"Кредит на оборотные средства","type":"Оборотный","description":"Для закупки товаров, покрытия кассовых разрывов и текущих расходов.","min_amount":100000,"max_amount":10000000,"term_months":36},
 {"id":"equipment","name":"Кредит на оборудование","type":"Инвестиционный","description":"Для покупки и обновления оборудования бизнеса.","min_amount":300000,"max_amount":20000000,"term_months":60},
 {"id":"growth","name":"Кредит на развитие бизнеса","type":"Развитие","description":"Для финансирования масштабирования и новых направлений.","min_amount":200000,"max_amount":15000000,"term_months":48}
]
@router.get("")
def products(user: User = Depends(current_user)):
    return PRODUCTS
@router.post("/recommend")
def recommend(payload: dict, user: User = Depends(current_user)):
    goal = str(payload.get("goal", "оборот"))
    if goal == "оборудование": items = [PRODUCTS[1], PRODUCTS[2]]
    elif goal == "развитие": items = [PRODUCTS[2], PRODUCTS[0]]
    else: items = [PRODUCTS[0], PRODUCTS[2]]
    amount = int(payload.get("amount", 1000000))
    items = [p for p in items if p["min_amount"] <= amount <= p["max_amount"]] or items
    return {"recommendations": items, "explanation": "Рекомендация сформирована по цели финансирования, сумме и желаемому сроку. Это демонстрационные правила, не банковское предложение."}
