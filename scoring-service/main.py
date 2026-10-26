from fastapi import FastAPI
from catboost import CatBoostClassifier
import pandas as pd
from catboost import Pool
from pydantic import BaseModel
from ollama import Client
from typing import List, Optional
import os

app = FastAPI(title="Кредитный помощник")
model = CatBoostClassifier()
model.load_model("model1.cbm")


client = Client(
    host=os.getenv("OLLAMA_HOST", "http://ollama:11434")
)


class ChatRequest(BaseModel):
    client_name: str

    Тип_продукта: str
    Сумма_кредита: float
    Срок_работы_мес: int
    Выручка_в_месяц: int
    Долговая_нагрузка_процент: int
    Просрочки: int
    Отрасль: str
    Счет_в_банке_мес: int

    решение: str
    риск: Optional[float] = None
    причина: Optional[str] = None


    user_message: str


def stop_result(reason: str):
    return {
        "решение": "Отказ (стоп-фактор)",
        "риск": None,
        "причина": reason,
        "источник_решения": "правило"
    }

@app.get("/")
def pon():
    return ('/docs')


@app.post("/score")
def get_score(data: dict):


    product =data.get("Тип_продукта")


    if product == "Оборотный":
        if data.get("Срок_работы_мес", 0) < 3:
            return stop_result("Деятельность менее 3 месяцев")
        if data.get("Просрочки") == 1:
            return stop_result("Просрочки за последние 12 месяцев")
        if data.get("Долговая_нагрузка_процент", 0) > 60:
            return stop_result( "ПДН свыше 60%")


    elif product == "Инвестиционный":
        if data.get("Срок_работы_мес", 0) < 12:
            return stop_result( "Деятельность менее  12 мес")
        if data.get("Сумма_кредита", 0) > 5_000_000 and data.get("LTV_залога", 0) == 0:
            return stop_result("Нет залога при сумме свыше 5 млн")


    elif product == "Овердрафт":
        if data.get("Счет_в_банке_мес", 0) < 6:
            return stop_result("Нет расчетного счета в банке более 6 месяцев ")
        if data.get("Оборот_в_месяц", 0) < 100_000:
            return stop_result("Среднемесячный оборот менее 100 тысяч ")
        if data.get("Долговая_нагрузка_процент", 0) > 55:
            return stop_result("ПДН свыше 55% ")



    elif product == "Сельскохозяйственный":
        if data.get("Срок_работы_мес", 0) < 12:
            return stop_result("Нет опыта в отрасли (менее 12 месяцев)")
        if data.get("Просрочки") == 1:
            return stop_result("Просрочки 30+ дней")
        if data.get("LTV_залога", 0) == 0:
            return stop_result("Отсутствие залога")
        if data.get("Долговая_нагрузка_процент", 0) > 50:
            return stop_result("ПДН свыше 50%")

    data_dict = {
        "Возраст_ИП": data.get("Возраст_ИП", 30),
        "Срок_работы_мес": data.get("Срок_работы_мес", 0),
        "Выручка_в_месяц": data.get("Выручка_в_месяц", 0),
        "Оборот_в_месяц": data.get("Оборот_в_месяц", 0),
        "Сотрудники": data.get("Сотрудники", 1),
        "Долговая_нагрузка_процент": data.get("Долговая_нагрузка_процент", 0),
        "Действующие_кредиты": data.get("Действующие_кредиты", 0),
        "Просрочки": data.get("Просрочки", 0),
        "Отрасль": data.get("Отрасль", "Прочее"),
        "Счет_в_банке_мес": data.get("Счет_в_банке_мес", 0)
    }


    features_order = [
        "Возраст_ИП", "Срок_работы_мес", "Выручка_в_месяц", "Оборот_в_месяц",
        "Сотрудники", "Долговая_нагрузка_процент", "Действующие_кредиты",
        "Просрочки", "Отрасль", "Счет_в_банке_мес"
    ]


    features = pd.DataFrame([data_dict])[features_order]



    prob = float(model.predict_proba(Pool(features, cat_features=["Отрасль"]))[0][0])




    if prob < 0.30:
        ds = "Одобрено (низкий риск)"
    elif prob < 0.60:
        ds = "Одобрено (средний риск)"
    else:
        ds = "Отказ (высокий риск)"

    return {
        "решение": ds,
        "риск": round(prob, 2),
        "причина": None,
        "источник_решения": "модель"
    }

@app.post('/chat')
async def LLM(data: ChatRequest):
    st = f"""
    Ты — ИИ-ассистент в личном кабинете предпринимателя {data.client_name}.
    Ты помогаешь ему разобраться с его заявкой на кредит.
    
    РЕШЕНИЕ ПО ЗАЯВКЕ: {data.решение}
    РИСК ПО ДЕМОНСТРАЦИОННОЙ МОДЕЛИ: {
        data.риск if data.риск is not None else "не рассчитан"
    }
    ПЕРЕДАННАЯ ПРИЧИНА: {data.причина or "не указана"}

    Правила ответа:
    - Используй только переданное решение и причину.
    - Не придумывай банковские правила, пороги, ставки и причины отказа.
    - Не называй заявку одобренной, если в поле решения прямо не указано одобрение.
    - Если причина не указана, честно скажи, что в переданных данных нет подробного объяснения.
    - Риск относится к демонстрационной модели на синтетических данных,
      а не к вероятности реального невозврата кредита.
    - Отвечай кратко, понятно и только на русском.

"""


    messages = [
        {'role': 'system', 'content': st},
        {'role': 'user', 'content': data.user_message}
    ]

    try:
        response = client.chat(model='qwen2.5:3b', messages=messages)
        reply_text = response.message.content
    except Exception:
        # загулшка если олама не работает
        reply_text = (
            f"По заявке указан статус: {data.решение}. "
            "Я временно не могу сформировать пояснение. "
            "Пожалуйста, ориентируйтесь на статус и причины, показанные в кабинете."
        )
    return {"reply": reply_text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9562
    )