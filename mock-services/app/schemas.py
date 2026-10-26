
from pydantic import BaseModel
class CheckRequest(BaseModel):
    inn: str
