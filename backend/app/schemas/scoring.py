
from pydantic import BaseModel, Field
class ScoringRequest(BaseModel):
    Тип_продукта: str
    Возраст_ИП: int
    Срок_работы_мес: int
    Выручка_в_месяц: int
    Оборот_в_месяц: int
    Сотрудники: int
    Долговая_нагрузка_процент: float
    Действующие_кредиты: int
    Просрочки: int
    Отрасль: str
    Счет_в_банке_мес: int
    LTV_залога: int
    Сумма_кредита: int
class ScoringResponse(BaseModel):
    риск: float = Field(ge=0, le=1)
    решение: str
