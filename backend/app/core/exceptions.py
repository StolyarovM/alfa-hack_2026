
from fastapi import HTTPException

def not_found(message: str = "Не найдено"):
    return HTTPException(status_code=404, detail=message)
