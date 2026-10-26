
export type ScoringRequest = {
  Тип_продукта: string; Возраст_ИП: number; Срок_работы_мес: number;
  Выручка_в_месяц: number; Оборот_в_месяц: number; Сотрудники: number;
  Долговая_нагрузка_процент: number; Действующие_кредиты: number; Просрочки: number;
  Отрасль: string; Счет_в_банке_мес: number; LTV_залога: number; Сумма_кредита: number;
};
export type ScoringResponse = { риск: number; решение: string };
