
def check_result(check_name: str, inn: str) -> dict:
    # ИНН, заканчивающийся на 999, имитирует сбой; остальные проходят тестовые проверки.
    if inn.endswith("999"):
        return {"ok": False, "status": "FAILED", "message": f"Не удалось выполнить проверку: {check_name}"}
    labels = {"registry":"Запись в реестре найдена", "credit-history":"Кредитная история получена", "financial":"Финансовые показатели получены"}
    return {"ok": True, "status": "PASSED", "message": labels.get(check_name, "Проверка пройдена")}
