
from pydantic import BaseModel, Field
class SurveyRequest(BaseModel):
    goal: str
    amount: int = Field(gt=0)
    term_months: int = Field(gt=0, le=120)
    urgency: str = "обычно"
