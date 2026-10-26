
from pydantic import BaseModel
class CompanyProfile(BaseModel):
    username: str
    inn: str
    business_name: str
    business_age_months: int
    industry: str
